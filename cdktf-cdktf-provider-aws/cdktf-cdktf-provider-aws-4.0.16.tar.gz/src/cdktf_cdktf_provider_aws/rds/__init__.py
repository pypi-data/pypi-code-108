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


class DataAwsDbClusterSnapshot(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbClusterSnapshot",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot aws_db_cluster_snapshot}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_cluster_identifier: typing.Optional[builtins.str] = None,
        db_cluster_snapshot_identifier: typing.Optional[builtins.str] = None,
        include_public: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_shared: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        most_recent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot aws_db_cluster_snapshot} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#db_cluster_identifier DataAwsDbClusterSnapshot#db_cluster_identifier}.
        :param db_cluster_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#db_cluster_snapshot_identifier DataAwsDbClusterSnapshot#db_cluster_snapshot_identifier}.
        :param include_public: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#include_public DataAwsDbClusterSnapshot#include_public}.
        :param include_shared: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#include_shared DataAwsDbClusterSnapshot#include_shared}.
        :param most_recent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#most_recent DataAwsDbClusterSnapshot#most_recent}.
        :param snapshot_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#snapshot_type DataAwsDbClusterSnapshot#snapshot_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#tags DataAwsDbClusterSnapshot#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDbClusterSnapshotConfig(
            db_cluster_identifier=db_cluster_identifier,
            db_cluster_snapshot_identifier=db_cluster_snapshot_identifier,
            include_public=include_public,
            include_shared=include_shared,
            most_recent=most_recent,
            snapshot_type=snapshot_type,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDbClusterIdentifier")
    def reset_db_cluster_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbClusterIdentifier", []))

    @jsii.member(jsii_name="resetDbClusterSnapshotIdentifier")
    def reset_db_cluster_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbClusterSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetIncludePublic")
    def reset_include_public(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludePublic", []))

    @jsii.member(jsii_name="resetIncludeShared")
    def reset_include_shared(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeShared", []))

    @jsii.member(jsii_name="resetMostRecent")
    def reset_most_recent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMostRecent", []))

    @jsii.member(jsii_name="resetSnapshotType")
    def reset_snapshot_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotType", []))

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
    @jsii.member(jsii_name="snapshotCreateTime")
    def snapshot_create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotCreateTime"))

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
    @jsii.member(jsii_name="includePublicInput")
    def include_public_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includePublicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeSharedInput")
    def include_shared_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeSharedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRecentInput")
    def most_recent_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "mostRecentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotTypeInput")
    def snapshot_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includePublic")
    def include_public(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includePublic"))

    @include_public.setter
    def include_public(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includePublic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeShared")
    def include_shared(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeShared"))

    @include_shared.setter
    def include_shared(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeShared", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRecent")
    def most_recent(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "mostRecent"))

    @most_recent.setter
    def most_recent(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "mostRecent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotType")
    def snapshot_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotType"))

    @snapshot_type.setter
    def snapshot_type(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotType", value)

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
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbClusterSnapshotConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_cluster_identifier": "dbClusterIdentifier",
        "db_cluster_snapshot_identifier": "dbClusterSnapshotIdentifier",
        "include_public": "includePublic",
        "include_shared": "includeShared",
        "most_recent": "mostRecent",
        "snapshot_type": "snapshotType",
        "tags": "tags",
    },
)
class DataAwsDbClusterSnapshotConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_cluster_identifier: typing.Optional[builtins.str] = None,
        db_cluster_snapshot_identifier: typing.Optional[builtins.str] = None,
        include_public: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_shared: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        most_recent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#db_cluster_identifier DataAwsDbClusterSnapshot#db_cluster_identifier}.
        :param db_cluster_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#db_cluster_snapshot_identifier DataAwsDbClusterSnapshot#db_cluster_snapshot_identifier}.
        :param include_public: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#include_public DataAwsDbClusterSnapshot#include_public}.
        :param include_shared: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#include_shared DataAwsDbClusterSnapshot#include_shared}.
        :param most_recent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#most_recent DataAwsDbClusterSnapshot#most_recent}.
        :param snapshot_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#snapshot_type DataAwsDbClusterSnapshot#snapshot_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#tags DataAwsDbClusterSnapshot#tags}.
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
        if db_cluster_identifier is not None:
            self._values["db_cluster_identifier"] = db_cluster_identifier
        if db_cluster_snapshot_identifier is not None:
            self._values["db_cluster_snapshot_identifier"] = db_cluster_snapshot_identifier
        if include_public is not None:
            self._values["include_public"] = include_public
        if include_shared is not None:
            self._values["include_shared"] = include_shared
        if most_recent is not None:
            self._values["most_recent"] = most_recent
        if snapshot_type is not None:
            self._values["snapshot_type"] = snapshot_type
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
    def db_cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#db_cluster_identifier DataAwsDbClusterSnapshot#db_cluster_identifier}.'''
        result = self._values.get("db_cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_cluster_snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#db_cluster_snapshot_identifier DataAwsDbClusterSnapshot#db_cluster_snapshot_identifier}.'''
        result = self._values.get("db_cluster_snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_public(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#include_public DataAwsDbClusterSnapshot#include_public}.'''
        result = self._values.get("include_public")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_shared(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#include_shared DataAwsDbClusterSnapshot#include_shared}.'''
        result = self._values.get("include_shared")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def most_recent(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#most_recent DataAwsDbClusterSnapshot#most_recent}.'''
        result = self._values.get("most_recent")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def snapshot_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#snapshot_type DataAwsDbClusterSnapshot#snapshot_type}.'''
        result = self._values.get("snapshot_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_cluster_snapshot#tags DataAwsDbClusterSnapshot#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDbClusterSnapshotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDbEventCategories(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbEventCategories",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/db_event_categories aws_db_event_categories}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        source_type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/db_event_categories aws_db_event_categories} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_event_categories#source_type DataAwsDbEventCategories#source_type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDbEventCategoriesConfig(
            source_type=source_type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetSourceType")
    def reset_source_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventCategories")
    def event_categories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventCategories"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceTypeInput")
    def source_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceType")
    def source_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceType"))

    @source_type.setter
    def source_type(self, value: builtins.str) -> None:
        jsii.set(self, "sourceType", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbEventCategoriesConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "source_type": "sourceType",
    },
)
class DataAwsDbEventCategoriesConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        source_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_event_categories#source_type DataAwsDbEventCategories#source_type}.
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
        if source_type is not None:
            self._values["source_type"] = source_type

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
    def source_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_event_categories#source_type DataAwsDbEventCategories#source_type}.'''
        result = self._values.get("source_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDbEventCategoriesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDbInstance(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/db_instance aws_db_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_instance_identifier: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/db_instance aws_db_instance} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_instance#db_instance_identifier DataAwsDbInstance#db_instance_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_instance#tags DataAwsDbInstance#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDbInstanceConfig(
            db_instance_identifier=db_instance_identifier,
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
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocatedStorage")
    def allocated_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "allocatedStorage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "autoMinorVersionUpgrade"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupRetentionPeriod"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caCertIdentifier")
    def ca_cert_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCertIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbClusterIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceArn")
    def db_instance_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceClass")
    def db_instance_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceClass"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstancePort")
    def db_instance_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "dbInstancePort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbName")
    def db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbParameterGroups")
    def db_parameter_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dbParameterGroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSecurityGroups")
    def db_security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dbSecurityGroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroup")
    def db_subnet_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbSubnetGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledCloudwatchLogsExports")
    def enabled_cloudwatch_logs_exports(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "enabledCloudwatchLogsExports"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseModel")
    def license_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseModel"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUsername")
    def master_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "masterUsername"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitoringInterval")
    def monitoring_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "monitoringInterval"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitoringRoleArn")
    def monitoring_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitoringRoleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAz")
    def multi_az(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "multiAz"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionGroupMemberships")
    def option_group_memberships(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "optionGroupMemberships"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredBackupWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredMaintenanceWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessible")
    def publicly_accessible(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "publiclyAccessible"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicateSourceDb")
    def replicate_source_db(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicateSourceDb"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "storageEncrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timezone")
    def timezone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroups")
    def vpc_security_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSecurityGroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifierInput")
    def db_instance_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbInstanceIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceIdentifier"))

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbInstanceIdentifier", value)

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
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_instance_identifier": "dbInstanceIdentifier",
        "tags": "tags",
    },
)
class DataAwsDbInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_instance_identifier: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_instance#db_instance_identifier DataAwsDbInstance#db_instance_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_instance#tags DataAwsDbInstance#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "db_instance_identifier": db_instance_identifier,
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
    def db_instance_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_instance#db_instance_identifier DataAwsDbInstance#db_instance_identifier}.'''
        result = self._values.get("db_instance_identifier")
        assert result is not None, "Required property 'db_instance_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_instance#tags DataAwsDbInstance#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDbInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDbProxy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbProxy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/db_proxy aws_db_proxy}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/db_proxy aws_db_proxy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_proxy#name DataAwsDbProxy#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDbProxyConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="auth")
    def auth(self, index: builtins.str) -> "DataAwsDbProxyAuth":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsDbProxyAuth", jsii.invoke(self, "auth", [index]))

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
    @jsii.member(jsii_name="debugLogging")
    def debug_logging(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "debugLogging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineFamily")
    def engine_family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineFamily"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleClientTimeout")
    def idle_client_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleClientTimeout"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireTls")
    def require_tls(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "requireTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSecurityGroupIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnetIds")
    def vpc_subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSubnetIds"))

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


class DataAwsDbProxyAuth(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbProxyAuth",
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
    @jsii.member(jsii_name="authScheme")
    def auth_scheme(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authScheme"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamAuth")
    def iam_auth(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamAuth"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretArn"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbProxyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsDbProxyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_proxy#name DataAwsDbProxy#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_proxy#name DataAwsDbProxy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDbProxyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDbSnapshot(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbSnapshot",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot aws_db_snapshot}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_instance_identifier: typing.Optional[builtins.str] = None,
        db_snapshot_identifier: typing.Optional[builtins.str] = None,
        include_public: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_shared: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        most_recent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot aws_db_snapshot} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#db_instance_identifier DataAwsDbSnapshot#db_instance_identifier}.
        :param db_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#db_snapshot_identifier DataAwsDbSnapshot#db_snapshot_identifier}.
        :param include_public: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#include_public DataAwsDbSnapshot#include_public}.
        :param include_shared: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#include_shared DataAwsDbSnapshot#include_shared}.
        :param most_recent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#most_recent DataAwsDbSnapshot#most_recent}.
        :param snapshot_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#snapshot_type DataAwsDbSnapshot#snapshot_type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDbSnapshotConfig(
            db_instance_identifier=db_instance_identifier,
            db_snapshot_identifier=db_snapshot_identifier,
            include_public=include_public,
            include_shared=include_shared,
            most_recent=most_recent,
            snapshot_type=snapshot_type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDbInstanceIdentifier")
    def reset_db_instance_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbInstanceIdentifier", []))

    @jsii.member(jsii_name="resetDbSnapshotIdentifier")
    def reset_db_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetIncludePublic")
    def reset_include_public(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludePublic", []))

    @jsii.member(jsii_name="resetIncludeShared")
    def reset_include_shared(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeShared", []))

    @jsii.member(jsii_name="resetMostRecent")
    def reset_most_recent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMostRecent", []))

    @jsii.member(jsii_name="resetSnapshotType")
    def reset_snapshot_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotType", []))

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
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSnapshotArn")
    def db_snapshot_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbSnapshotArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "encrypted"))

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
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseModel")
    def license_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseModel"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionGroupName")
    def option_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "optionGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotCreateTime")
    def snapshot_create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotCreateTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDbSnapshotIdentifier")
    def source_db_snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDbSnapshotIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceRegion")
    def source_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceRegion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifierInput")
    def db_instance_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbInstanceIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSnapshotIdentifierInput")
    def db_snapshot_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbSnapshotIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includePublicInput")
    def include_public_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includePublicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeSharedInput")
    def include_shared_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeSharedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRecentInput")
    def most_recent_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "mostRecentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotTypeInput")
    def snapshot_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceIdentifier"))

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbInstanceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSnapshotIdentifier")
    def db_snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbSnapshotIdentifier"))

    @db_snapshot_identifier.setter
    def db_snapshot_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbSnapshotIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includePublic")
    def include_public(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includePublic"))

    @include_public.setter
    def include_public(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includePublic", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeShared")
    def include_shared(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeShared"))

    @include_shared.setter
    def include_shared(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeShared", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRecent")
    def most_recent(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "mostRecent"))

    @most_recent.setter
    def most_recent(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "mostRecent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotType")
    def snapshot_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotType"))

    @snapshot_type.setter
    def snapshot_type(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotType", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbSnapshotConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_instance_identifier": "dbInstanceIdentifier",
        "db_snapshot_identifier": "dbSnapshotIdentifier",
        "include_public": "includePublic",
        "include_shared": "includeShared",
        "most_recent": "mostRecent",
        "snapshot_type": "snapshotType",
    },
)
class DataAwsDbSnapshotConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_instance_identifier: typing.Optional[builtins.str] = None,
        db_snapshot_identifier: typing.Optional[builtins.str] = None,
        include_public: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_shared: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        most_recent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#db_instance_identifier DataAwsDbSnapshot#db_instance_identifier}.
        :param db_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#db_snapshot_identifier DataAwsDbSnapshot#db_snapshot_identifier}.
        :param include_public: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#include_public DataAwsDbSnapshot#include_public}.
        :param include_shared: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#include_shared DataAwsDbSnapshot#include_shared}.
        :param most_recent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#most_recent DataAwsDbSnapshot#most_recent}.
        :param snapshot_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#snapshot_type DataAwsDbSnapshot#snapshot_type}.
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
        if db_instance_identifier is not None:
            self._values["db_instance_identifier"] = db_instance_identifier
        if db_snapshot_identifier is not None:
            self._values["db_snapshot_identifier"] = db_snapshot_identifier
        if include_public is not None:
            self._values["include_public"] = include_public
        if include_shared is not None:
            self._values["include_shared"] = include_shared
        if most_recent is not None:
            self._values["most_recent"] = most_recent
        if snapshot_type is not None:
            self._values["snapshot_type"] = snapshot_type

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
    def db_instance_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#db_instance_identifier DataAwsDbSnapshot#db_instance_identifier}.'''
        result = self._values.get("db_instance_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#db_snapshot_identifier DataAwsDbSnapshot#db_snapshot_identifier}.'''
        result = self._values.get("db_snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_public(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#include_public DataAwsDbSnapshot#include_public}.'''
        result = self._values.get("include_public")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_shared(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#include_shared DataAwsDbSnapshot#include_shared}.'''
        result = self._values.get("include_shared")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def most_recent(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#most_recent DataAwsDbSnapshot#most_recent}.'''
        result = self._values.get("most_recent")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def snapshot_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_snapshot#snapshot_type DataAwsDbSnapshot#snapshot_type}.'''
        result = self._values.get("snapshot_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDbSnapshotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDbSubnetGroup(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbSubnetGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/db_subnet_group aws_db_subnet_group}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/db_subnet_group aws_db_subnet_group} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_subnet_group#name DataAwsDbSubnetGroup#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDbSubnetGroupConfig(
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
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

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
    jsii_type="@cdktf/provider-aws.rds.DataAwsDbSubnetGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsDbSubnetGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_subnet_group#name DataAwsDbSubnetGroup#name}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/db_subnet_group#name DataAwsDbSubnetGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDbSubnetGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsRdsCertificate(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsRdsCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/rds_certificate aws_rds_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        latest_valid_till: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/rds_certificate aws_rds_certificate} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param latest_valid_till: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_certificate#latest_valid_till DataAwsRdsCertificate#latest_valid_till}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsRdsCertificateConfig(
            latest_valid_till=latest_valid_till,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetLatestValidTill")
    def reset_latest_valid_till(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLatestValidTill", []))

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
    @jsii.member(jsii_name="certificateType")
    def certificate_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerOverride")
    def customer_override(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "customerOverride"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerOverrideValidTill")
    def customer_override_valid_till(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerOverrideValidTill"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thumbprint")
    def thumbprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "thumbprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validFrom")
    def valid_from(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validFrom"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validTill")
    def valid_till(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validTill"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestValidTillInput")
    def latest_valid_till_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "latestValidTillInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestValidTill")
    def latest_valid_till(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "latestValidTill"))

    @latest_valid_till.setter
    def latest_valid_till(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "latestValidTill", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DataAwsRdsCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "latest_valid_till": "latestValidTill",
    },
)
class DataAwsRdsCertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        latest_valid_till: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param latest_valid_till: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_certificate#latest_valid_till DataAwsRdsCertificate#latest_valid_till}.
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
        if latest_valid_till is not None:
            self._values["latest_valid_till"] = latest_valid_till

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
    def latest_valid_till(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_certificate#latest_valid_till DataAwsRdsCertificate#latest_valid_till}.'''
        result = self._values.get("latest_valid_till")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsRdsCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsRdsCluster(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsRdsCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/rds_cluster aws_rds_cluster}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/rds_cluster aws_rds_cluster} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_cluster#cluster_identifier DataAwsRdsCluster#cluster_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_cluster#tags DataAwsRdsCluster#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsRdsClusterConfig(
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZones")
    def availability_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "availabilityZones"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backtrackWindow")
    def backtrack_window(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backtrackWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupRetentionPeriod"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterMembers")
    def cluster_members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clusterMembers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterResourceId")
    def cluster_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterResourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterParameterGroupName")
    def db_cluster_parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbClusterParameterGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbSubnetGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledCloudwatchLogsExports")
    def enabled_cloudwatch_logs_exports(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "enabledCloudwatchLogsExports"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="finalSnapshotIdentifier")
    def final_snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "finalSnapshotIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamDatabaseAuthenticationEnabled")
    def iam_database_authentication_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "iamDatabaseAuthenticationEnabled"))

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
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredBackupWindow")
    def preferred_backup_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredBackupWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredMaintenanceWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readerEndpoint")
    def reader_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readerEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationSourceIdentifier")
    def replication_source_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationSourceIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "storageEncrypted"))

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
    jsii_type="@cdktf/provider-aws.rds.DataAwsRdsClusterConfig",
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
class DataAwsRdsClusterConfig(cdktf.TerraformMetaArguments):
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
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_cluster#cluster_identifier DataAwsRdsCluster#cluster_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_cluster#tags DataAwsRdsCluster#tags}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_cluster#cluster_identifier DataAwsRdsCluster#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_cluster#tags DataAwsRdsCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsRdsClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsRdsEngineVersion(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsRdsEngineVersion",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version aws_rds_engine_version}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        engine: builtins.str,
        parameter_group_family: typing.Optional[builtins.str] = None,
        preferred_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version aws_rds_engine_version} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#engine DataAwsRdsEngineVersion#engine}.
        :param parameter_group_family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#parameter_group_family DataAwsRdsEngineVersion#parameter_group_family}.
        :param preferred_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#preferred_versions DataAwsRdsEngineVersion#preferred_versions}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#version DataAwsRdsEngineVersion#version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsRdsEngineVersionConfig(
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
    @jsii.member(jsii_name="defaultCharacterSet")
    def default_character_set(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultCharacterSet"))

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
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedCharacterSets")
    def supported_character_sets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedCharacterSets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedFeatureNames")
    def supported_feature_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedFeatureNames"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedModes")
    def supported_modes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedModes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedTimezones")
    def supported_timezones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedTimezones"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsGlobalDatabases")
    def supports_global_databases(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsGlobalDatabases"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsLogExportsToCloudwatch")
    def supports_log_exports_to_cloudwatch(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsLogExportsToCloudwatch"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsParallelQuery")
    def supports_parallel_query(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "supportsParallelQuery"))

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
    jsii_type="@cdktf/provider-aws.rds.DataAwsRdsEngineVersionConfig",
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
class DataAwsRdsEngineVersionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        engine: builtins.str,
        parameter_group_family: typing.Optional[builtins.str] = None,
        preferred_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#engine DataAwsRdsEngineVersion#engine}.
        :param parameter_group_family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#parameter_group_family DataAwsRdsEngineVersion#parameter_group_family}.
        :param preferred_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#preferred_versions DataAwsRdsEngineVersion#preferred_versions}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#version DataAwsRdsEngineVersion#version}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "engine": engine,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
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
    def engine(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#engine DataAwsRdsEngineVersion#engine}.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_group_family(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#parameter_group_family DataAwsRdsEngineVersion#parameter_group_family}.'''
        result = self._values.get("parameter_group_family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#preferred_versions DataAwsRdsEngineVersion#preferred_versions}.'''
        result = self._values.get("preferred_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_engine_version#version DataAwsRdsEngineVersion#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsRdsEngineVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsRdsOrderableDbInstance(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DataAwsRdsOrderableDbInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance aws_rds_orderable_db_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        engine: builtins.str,
        availability_zone_group: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        instance_class: typing.Optional[builtins.str] = None,
        license_model: typing.Optional[builtins.str] = None,
        preferred_engine_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_instance_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_type: typing.Optional[builtins.str] = None,
        supports_enhanced_monitoring: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_global_databases: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_iam_database_authentication: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_iops: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_kerberos_authentication: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_performance_insights: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_storage_autoscaling: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_storage_encryption: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        vpc: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance aws_rds_orderable_db_instance} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#engine DataAwsRdsOrderableDbInstance#engine}.
        :param availability_zone_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#availability_zone_group DataAwsRdsOrderableDbInstance#availability_zone_group}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#engine_version DataAwsRdsOrderableDbInstance#engine_version}.
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#instance_class DataAwsRdsOrderableDbInstance#instance_class}.
        :param license_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#license_model DataAwsRdsOrderableDbInstance#license_model}.
        :param preferred_engine_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#preferred_engine_versions DataAwsRdsOrderableDbInstance#preferred_engine_versions}.
        :param preferred_instance_classes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#preferred_instance_classes DataAwsRdsOrderableDbInstance#preferred_instance_classes}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#storage_type DataAwsRdsOrderableDbInstance#storage_type}.
        :param supports_enhanced_monitoring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_enhanced_monitoring DataAwsRdsOrderableDbInstance#supports_enhanced_monitoring}.
        :param supports_global_databases: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_global_databases DataAwsRdsOrderableDbInstance#supports_global_databases}.
        :param supports_iam_database_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_iam_database_authentication DataAwsRdsOrderableDbInstance#supports_iam_database_authentication}.
        :param supports_iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_iops DataAwsRdsOrderableDbInstance#supports_iops}.
        :param supports_kerberos_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_kerberos_authentication DataAwsRdsOrderableDbInstance#supports_kerberos_authentication}.
        :param supports_performance_insights: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_performance_insights DataAwsRdsOrderableDbInstance#supports_performance_insights}.
        :param supports_storage_autoscaling: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_storage_autoscaling DataAwsRdsOrderableDbInstance#supports_storage_autoscaling}.
        :param supports_storage_encryption: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_storage_encryption DataAwsRdsOrderableDbInstance#supports_storage_encryption}.
        :param vpc: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#vpc DataAwsRdsOrderableDbInstance#vpc}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsRdsOrderableDbInstanceConfig(
            engine=engine,
            availability_zone_group=availability_zone_group,
            engine_version=engine_version,
            instance_class=instance_class,
            license_model=license_model,
            preferred_engine_versions=preferred_engine_versions,
            preferred_instance_classes=preferred_instance_classes,
            storage_type=storage_type,
            supports_enhanced_monitoring=supports_enhanced_monitoring,
            supports_global_databases=supports_global_databases,
            supports_iam_database_authentication=supports_iam_database_authentication,
            supports_iops=supports_iops,
            supports_kerberos_authentication=supports_kerberos_authentication,
            supports_performance_insights=supports_performance_insights,
            supports_storage_autoscaling=supports_storage_autoscaling,
            supports_storage_encryption=supports_storage_encryption,
            vpc=vpc,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAvailabilityZoneGroup")
    def reset_availability_zone_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZoneGroup", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetInstanceClass")
    def reset_instance_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceClass", []))

    @jsii.member(jsii_name="resetLicenseModel")
    def reset_license_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLicenseModel", []))

    @jsii.member(jsii_name="resetPreferredEngineVersions")
    def reset_preferred_engine_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredEngineVersions", []))

    @jsii.member(jsii_name="resetPreferredInstanceClasses")
    def reset_preferred_instance_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredInstanceClasses", []))

    @jsii.member(jsii_name="resetStorageType")
    def reset_storage_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageType", []))

    @jsii.member(jsii_name="resetSupportsEnhancedMonitoring")
    def reset_supports_enhanced_monitoring(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportsEnhancedMonitoring", []))

    @jsii.member(jsii_name="resetSupportsGlobalDatabases")
    def reset_supports_global_databases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportsGlobalDatabases", []))

    @jsii.member(jsii_name="resetSupportsIamDatabaseAuthentication")
    def reset_supports_iam_database_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportsIamDatabaseAuthentication", []))

    @jsii.member(jsii_name="resetSupportsIops")
    def reset_supports_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportsIops", []))

    @jsii.member(jsii_name="resetSupportsKerberosAuthentication")
    def reset_supports_kerberos_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportsKerberosAuthentication", []))

    @jsii.member(jsii_name="resetSupportsPerformanceInsights")
    def reset_supports_performance_insights(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportsPerformanceInsights", []))

    @jsii.member(jsii_name="resetSupportsStorageAutoscaling")
    def reset_supports_storage_autoscaling(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportsStorageAutoscaling", []))

    @jsii.member(jsii_name="resetSupportsStorageEncryption")
    def reset_supports_storage_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSupportsStorageEncryption", []))

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
    @jsii.member(jsii_name="outpostCapable")
    def outpost_capable(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "outpostCapable"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readReplicaCapable")
    def read_replica_capable(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "readReplicaCapable"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportedEngineModes")
    def supported_engine_modes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "supportedEngineModes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneGroupInput")
    def availability_zone_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneGroupInput"))

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
    @jsii.member(jsii_name="preferredEngineVersionsInput")
    def preferred_engine_versions_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredEngineVersionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredInstanceClassesInput")
    def preferred_instance_classes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "preferredInstanceClassesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageTypeInput")
    def storage_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsEnhancedMonitoringInput")
    def supports_enhanced_monitoring_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "supportsEnhancedMonitoringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsGlobalDatabasesInput")
    def supports_global_databases_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "supportsGlobalDatabasesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsIamDatabaseAuthenticationInput")
    def supports_iam_database_authentication_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "supportsIamDatabaseAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsIopsInput")
    def supports_iops_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "supportsIopsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsKerberosAuthenticationInput")
    def supports_kerberos_authentication_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "supportsKerberosAuthenticationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsPerformanceInsightsInput")
    def supports_performance_insights_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "supportsPerformanceInsightsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsStorageAutoscalingInput")
    def supports_storage_autoscaling_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "supportsStorageAutoscalingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsStorageEncryptionInput")
    def supports_storage_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "supportsStorageEncryptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcInput")
    def vpc_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "vpcInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneGroup")
    def availability_zone_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZoneGroup"))

    @availability_zone_group.setter
    def availability_zone_group(self, value: builtins.str) -> None:
        jsii.set(self, "availabilityZoneGroup", value)

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
    @jsii.member(jsii_name="preferredEngineVersions")
    def preferred_engine_versions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredEngineVersions"))

    @preferred_engine_versions.setter
    def preferred_engine_versions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "preferredEngineVersions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preferredInstanceClasses")
    def preferred_instance_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "preferredInstanceClasses"))

    @preferred_instance_classes.setter
    def preferred_instance_classes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "preferredInstanceClasses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @storage_type.setter
    def storage_type(self, value: builtins.str) -> None:
        jsii.set(self, "storageType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsEnhancedMonitoring")
    def supports_enhanced_monitoring(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "supportsEnhancedMonitoring"))

    @supports_enhanced_monitoring.setter
    def supports_enhanced_monitoring(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "supportsEnhancedMonitoring", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsGlobalDatabases")
    def supports_global_databases(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "supportsGlobalDatabases"))

    @supports_global_databases.setter
    def supports_global_databases(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "supportsGlobalDatabases", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsIamDatabaseAuthentication")
    def supports_iam_database_authentication(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "supportsIamDatabaseAuthentication"))

    @supports_iam_database_authentication.setter
    def supports_iam_database_authentication(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "supportsIamDatabaseAuthentication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsIops")
    def supports_iops(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "supportsIops"))

    @supports_iops.setter
    def supports_iops(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "supportsIops", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsKerberosAuthentication")
    def supports_kerberos_authentication(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "supportsKerberosAuthentication"))

    @supports_kerberos_authentication.setter
    def supports_kerberos_authentication(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "supportsKerberosAuthentication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsPerformanceInsights")
    def supports_performance_insights(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "supportsPerformanceInsights"))

    @supports_performance_insights.setter
    def supports_performance_insights(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "supportsPerformanceInsights", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsStorageAutoscaling")
    def supports_storage_autoscaling(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "supportsStorageAutoscaling"))

    @supports_storage_autoscaling.setter
    def supports_storage_autoscaling(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "supportsStorageAutoscaling", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportsStorageEncryption")
    def supports_storage_encryption(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "supportsStorageEncryption"))

    @supports_storage_encryption.setter
    def supports_storage_encryption(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "supportsStorageEncryption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "vpc", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DataAwsRdsOrderableDbInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "engine": "engine",
        "availability_zone_group": "availabilityZoneGroup",
        "engine_version": "engineVersion",
        "instance_class": "instanceClass",
        "license_model": "licenseModel",
        "preferred_engine_versions": "preferredEngineVersions",
        "preferred_instance_classes": "preferredInstanceClasses",
        "storage_type": "storageType",
        "supports_enhanced_monitoring": "supportsEnhancedMonitoring",
        "supports_global_databases": "supportsGlobalDatabases",
        "supports_iam_database_authentication": "supportsIamDatabaseAuthentication",
        "supports_iops": "supportsIops",
        "supports_kerberos_authentication": "supportsKerberosAuthentication",
        "supports_performance_insights": "supportsPerformanceInsights",
        "supports_storage_autoscaling": "supportsStorageAutoscaling",
        "supports_storage_encryption": "supportsStorageEncryption",
        "vpc": "vpc",
    },
)
class DataAwsRdsOrderableDbInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        engine: builtins.str,
        availability_zone_group: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        instance_class: typing.Optional[builtins.str] = None,
        license_model: typing.Optional[builtins.str] = None,
        preferred_engine_versions: typing.Optional[typing.Sequence[builtins.str]] = None,
        preferred_instance_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        storage_type: typing.Optional[builtins.str] = None,
        supports_enhanced_monitoring: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_global_databases: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_iam_database_authentication: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_iops: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_kerberos_authentication: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_performance_insights: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_storage_autoscaling: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        supports_storage_encryption: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        vpc: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#engine DataAwsRdsOrderableDbInstance#engine}.
        :param availability_zone_group: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#availability_zone_group DataAwsRdsOrderableDbInstance#availability_zone_group}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#engine_version DataAwsRdsOrderableDbInstance#engine_version}.
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#instance_class DataAwsRdsOrderableDbInstance#instance_class}.
        :param license_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#license_model DataAwsRdsOrderableDbInstance#license_model}.
        :param preferred_engine_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#preferred_engine_versions DataAwsRdsOrderableDbInstance#preferred_engine_versions}.
        :param preferred_instance_classes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#preferred_instance_classes DataAwsRdsOrderableDbInstance#preferred_instance_classes}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#storage_type DataAwsRdsOrderableDbInstance#storage_type}.
        :param supports_enhanced_monitoring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_enhanced_monitoring DataAwsRdsOrderableDbInstance#supports_enhanced_monitoring}.
        :param supports_global_databases: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_global_databases DataAwsRdsOrderableDbInstance#supports_global_databases}.
        :param supports_iam_database_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_iam_database_authentication DataAwsRdsOrderableDbInstance#supports_iam_database_authentication}.
        :param supports_iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_iops DataAwsRdsOrderableDbInstance#supports_iops}.
        :param supports_kerberos_authentication: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_kerberos_authentication DataAwsRdsOrderableDbInstance#supports_kerberos_authentication}.
        :param supports_performance_insights: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_performance_insights DataAwsRdsOrderableDbInstance#supports_performance_insights}.
        :param supports_storage_autoscaling: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_storage_autoscaling DataAwsRdsOrderableDbInstance#supports_storage_autoscaling}.
        :param supports_storage_encryption: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_storage_encryption DataAwsRdsOrderableDbInstance#supports_storage_encryption}.
        :param vpc: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#vpc DataAwsRdsOrderableDbInstance#vpc}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "engine": engine,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if availability_zone_group is not None:
            self._values["availability_zone_group"] = availability_zone_group
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if instance_class is not None:
            self._values["instance_class"] = instance_class
        if license_model is not None:
            self._values["license_model"] = license_model
        if preferred_engine_versions is not None:
            self._values["preferred_engine_versions"] = preferred_engine_versions
        if preferred_instance_classes is not None:
            self._values["preferred_instance_classes"] = preferred_instance_classes
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if supports_enhanced_monitoring is not None:
            self._values["supports_enhanced_monitoring"] = supports_enhanced_monitoring
        if supports_global_databases is not None:
            self._values["supports_global_databases"] = supports_global_databases
        if supports_iam_database_authentication is not None:
            self._values["supports_iam_database_authentication"] = supports_iam_database_authentication
        if supports_iops is not None:
            self._values["supports_iops"] = supports_iops
        if supports_kerberos_authentication is not None:
            self._values["supports_kerberos_authentication"] = supports_kerberos_authentication
        if supports_performance_insights is not None:
            self._values["supports_performance_insights"] = supports_performance_insights
        if supports_storage_autoscaling is not None:
            self._values["supports_storage_autoscaling"] = supports_storage_autoscaling
        if supports_storage_encryption is not None:
            self._values["supports_storage_encryption"] = supports_storage_encryption
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
    def engine(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#engine DataAwsRdsOrderableDbInstance#engine}.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def availability_zone_group(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#availability_zone_group DataAwsRdsOrderableDbInstance#availability_zone_group}.'''
        result = self._values.get("availability_zone_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#engine_version DataAwsRdsOrderableDbInstance#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#instance_class DataAwsRdsOrderableDbInstance#instance_class}.'''
        result = self._values.get("instance_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license_model(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#license_model DataAwsRdsOrderableDbInstance#license_model}.'''
        result = self._values.get("license_model")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_engine_versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#preferred_engine_versions DataAwsRdsOrderableDbInstance#preferred_engine_versions}.'''
        result = self._values.get("preferred_engine_versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def preferred_instance_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#preferred_instance_classes DataAwsRdsOrderableDbInstance#preferred_instance_classes}.'''
        result = self._values.get("preferred_instance_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#storage_type DataAwsRdsOrderableDbInstance#storage_type}.'''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def supports_enhanced_monitoring(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_enhanced_monitoring DataAwsRdsOrderableDbInstance#supports_enhanced_monitoring}.'''
        result = self._values.get("supports_enhanced_monitoring")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def supports_global_databases(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_global_databases DataAwsRdsOrderableDbInstance#supports_global_databases}.'''
        result = self._values.get("supports_global_databases")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def supports_iam_database_authentication(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_iam_database_authentication DataAwsRdsOrderableDbInstance#supports_iam_database_authentication}.'''
        result = self._values.get("supports_iam_database_authentication")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def supports_iops(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_iops DataAwsRdsOrderableDbInstance#supports_iops}.'''
        result = self._values.get("supports_iops")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def supports_kerberos_authentication(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_kerberos_authentication DataAwsRdsOrderableDbInstance#supports_kerberos_authentication}.'''
        result = self._values.get("supports_kerberos_authentication")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def supports_performance_insights(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_performance_insights DataAwsRdsOrderableDbInstance#supports_performance_insights}.'''
        result = self._values.get("supports_performance_insights")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def supports_storage_autoscaling(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_storage_autoscaling DataAwsRdsOrderableDbInstance#supports_storage_autoscaling}.'''
        result = self._values.get("supports_storage_autoscaling")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def supports_storage_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#supports_storage_encryption DataAwsRdsOrderableDbInstance#supports_storage_encryption}.'''
        result = self._values.get("supports_storage_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/rds_orderable_db_instance#vpc DataAwsRdsOrderableDbInstance#vpc}.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsRdsOrderableDbInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbClusterSnapshot(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbClusterSnapshot",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot aws_db_cluster_snapshot}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_cluster_identifier: builtins.str,
        db_cluster_snapshot_identifier: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbClusterSnapshotTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot aws_db_cluster_snapshot} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#db_cluster_identifier DbClusterSnapshot#db_cluster_identifier}.
        :param db_cluster_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#db_cluster_snapshot_identifier DbClusterSnapshot#db_cluster_snapshot_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#tags DbClusterSnapshot#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#tags_all DbClusterSnapshot#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#timeouts DbClusterSnapshot#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbClusterSnapshotConfig(
            db_cluster_identifier=db_cluster_identifier,
            db_cluster_snapshot_identifier=db_cluster_snapshot_identifier,
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
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#create DbClusterSnapshot#create}.
        '''
        value = DbClusterSnapshotTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

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
    def timeouts(self) -> "DbClusterSnapshotTimeoutsOutputReference":
        return typing.cast("DbClusterSnapshotTimeoutsOutputReference", jsii.get(self, "timeouts"))

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
    def timeouts_input(self) -> typing.Optional["DbClusterSnapshotTimeouts"]:
        return typing.cast(typing.Optional["DbClusterSnapshotTimeouts"], jsii.get(self, "timeoutsInput"))

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
    jsii_type="@cdktf/provider-aws.rds.DbClusterSnapshotConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_cluster_identifier": "dbClusterIdentifier",
        "db_cluster_snapshot_identifier": "dbClusterSnapshotIdentifier",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class DbClusterSnapshotConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_cluster_identifier: builtins.str,
        db_cluster_snapshot_identifier: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbClusterSnapshotTimeouts"] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#db_cluster_identifier DbClusterSnapshot#db_cluster_identifier}.
        :param db_cluster_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#db_cluster_snapshot_identifier DbClusterSnapshot#db_cluster_snapshot_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#tags DbClusterSnapshot#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#tags_all DbClusterSnapshot#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#timeouts DbClusterSnapshot#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DbClusterSnapshotTimeouts(**timeouts)
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
    def db_cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#db_cluster_identifier DbClusterSnapshot#db_cluster_identifier}.'''
        result = self._values.get("db_cluster_identifier")
        assert result is not None, "Required property 'db_cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_cluster_snapshot_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#db_cluster_snapshot_identifier DbClusterSnapshot#db_cluster_snapshot_identifier}.'''
        result = self._values.get("db_cluster_snapshot_identifier")
        assert result is not None, "Required property 'db_cluster_snapshot_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#tags DbClusterSnapshot#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#tags_all DbClusterSnapshot#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DbClusterSnapshotTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#timeouts DbClusterSnapshot#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DbClusterSnapshotTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbClusterSnapshotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbClusterSnapshotTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class DbClusterSnapshotTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#create DbClusterSnapshot#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_cluster_snapshot#create DbClusterSnapshot#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbClusterSnapshotTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbClusterSnapshotTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbClusterSnapshotTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[DbClusterSnapshotTimeouts]:
        return typing.cast(typing.Optional[DbClusterSnapshotTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DbClusterSnapshotTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class DbEventSubscription(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbEventSubscription",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription aws_db_event_subscription}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        sns_topic: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbEventSubscriptionTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription aws_db_event_subscription} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param sns_topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#sns_topic DbEventSubscription#sns_topic}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#enabled DbEventSubscription#enabled}.
        :param event_categories: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#event_categories DbEventSubscription#event_categories}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#name DbEventSubscription#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#name_prefix DbEventSubscription#name_prefix}.
        :param source_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#source_ids DbEventSubscription#source_ids}.
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#source_type DbEventSubscription#source_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#tags DbEventSubscription#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#tags_all DbEventSubscription#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#timeouts DbEventSubscription#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbEventSubscriptionConfig(
            sns_topic=sns_topic,
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
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#create DbEventSubscription#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#delete DbEventSubscription#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#update DbEventSubscription#update}.
        '''
        value = DbEventSubscriptionTimeouts(
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
    def timeouts(self) -> "DbEventSubscriptionTimeoutsOutputReference":
        return typing.cast("DbEventSubscriptionTimeoutsOutputReference", jsii.get(self, "timeouts"))

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
    @jsii.member(jsii_name="snsTopicInput")
    def sns_topic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicInput"))

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
    def timeouts_input(self) -> typing.Optional["DbEventSubscriptionTimeouts"]:
        return typing.cast(typing.Optional["DbEventSubscriptionTimeouts"], jsii.get(self, "timeoutsInput"))

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
    @jsii.member(jsii_name="snsTopic")
    def sns_topic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopic"))

    @sns_topic.setter
    def sns_topic(self, value: builtins.str) -> None:
        jsii.set(self, "snsTopic", value)

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
    jsii_type="@cdktf/provider-aws.rds.DbEventSubscriptionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "sns_topic": "snsTopic",
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
class DbEventSubscriptionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        sns_topic: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        event_categories: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        source_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        source_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbEventSubscriptionTimeouts"] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param sns_topic: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#sns_topic DbEventSubscription#sns_topic}.
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#enabled DbEventSubscription#enabled}.
        :param event_categories: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#event_categories DbEventSubscription#event_categories}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#name DbEventSubscription#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#name_prefix DbEventSubscription#name_prefix}.
        :param source_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#source_ids DbEventSubscription#source_ids}.
        :param source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#source_type DbEventSubscription#source_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#tags DbEventSubscription#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#tags_all DbEventSubscription#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#timeouts DbEventSubscription#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DbEventSubscriptionTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "sns_topic": sns_topic,
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
    def sns_topic(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#sns_topic DbEventSubscription#sns_topic}.'''
        result = self._values.get("sns_topic")
        assert result is not None, "Required property 'sns_topic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#enabled DbEventSubscription#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def event_categories(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#event_categories DbEventSubscription#event_categories}.'''
        result = self._values.get("event_categories")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#name DbEventSubscription#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#name_prefix DbEventSubscription#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#source_ids DbEventSubscription#source_ids}.'''
        result = self._values.get("source_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def source_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#source_type DbEventSubscription#source_type}.'''
        result = self._values.get("source_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#tags DbEventSubscription#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#tags_all DbEventSubscription#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DbEventSubscriptionTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#timeouts DbEventSubscription#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DbEventSubscriptionTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbEventSubscriptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbEventSubscriptionTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class DbEventSubscriptionTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#create DbEventSubscription#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#delete DbEventSubscription#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#update DbEventSubscription#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#create DbEventSubscription#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#delete DbEventSubscription#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_event_subscription#update DbEventSubscription#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbEventSubscriptionTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbEventSubscriptionTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbEventSubscriptionTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[DbEventSubscriptionTimeouts]:
        return typing.cast(typing.Optional[DbEventSubscriptionTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DbEventSubscriptionTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DbInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_instance aws_db_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        instance_class: builtins.str,
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        backup_retention_period: typing.Optional[jsii.Number] = None,
        backup_window: typing.Optional[builtins.str] = None,
        ca_cert_identifier: typing.Optional[builtins.str] = None,
        character_set_name: typing.Optional[builtins.str] = None,
        copy_tags_to_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        customer_owned_ip_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        delete_automated_backups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_iam_role_name: typing.Optional[builtins.str] = None,
        enabled_cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        iam_database_authentication_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        identifier: typing.Optional[builtins.str] = None,
        identifier_prefix: typing.Optional[builtins.str] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        license_model: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        max_allocated_storage: typing.Optional[jsii.Number] = None,
        monitoring_interval: typing.Optional[jsii.Number] = None,
        monitoring_role_arn: typing.Optional[builtins.str] = None,
        multi_az: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        nchar_character_set_name: typing.Optional[builtins.str] = None,
        option_group_name: typing.Optional[builtins.str] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        performance_insights_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        performance_insights_kms_key_id: typing.Optional[builtins.str] = None,
        performance_insights_retention_period: typing.Optional[jsii.Number] = None,
        port: typing.Optional[jsii.Number] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        replica_mode: typing.Optional[builtins.str] = None,
        replicate_source_db: typing.Optional[builtins.str] = None,
        restore_to_point_in_time: typing.Optional["DbInstanceRestoreToPointInTime"] = None,
        s3_import: typing.Optional["DbInstanceS3Import"] = None,
        security_group_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        skip_final_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbInstanceTimeouts"] = None,
        timezone: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_instance aws_db_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#instance_class DbInstance#instance_class}.
        :param allocated_storage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#allocated_storage DbInstance#allocated_storage}.
        :param allow_major_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#allow_major_version_upgrade DbInstance#allow_major_version_upgrade}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#apply_immediately DbInstance#apply_immediately}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#auto_minor_version_upgrade DbInstance#auto_minor_version_upgrade}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#availability_zone DbInstance#availability_zone}.
        :param backup_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#backup_retention_period DbInstance#backup_retention_period}.
        :param backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#backup_window DbInstance#backup_window}.
        :param ca_cert_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#ca_cert_identifier DbInstance#ca_cert_identifier}.
        :param character_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#character_set_name DbInstance#character_set_name}.
        :param copy_tags_to_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#copy_tags_to_snapshot DbInstance#copy_tags_to_snapshot}.
        :param customer_owned_ip_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#customer_owned_ip_enabled DbInstance#customer_owned_ip_enabled}.
        :param db_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#db_subnet_group_name DbInstance#db_subnet_group_name}.
        :param delete_automated_backups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#delete_automated_backups DbInstance#delete_automated_backups}.
        :param deletion_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#deletion_protection DbInstance#deletion_protection}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#domain DbInstance#domain}.
        :param domain_iam_role_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#domain_iam_role_name DbInstance#domain_iam_role_name}.
        :param enabled_cloudwatch_logs_exports: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#enabled_cloudwatch_logs_exports DbInstance#enabled_cloudwatch_logs_exports}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#engine DbInstance#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#engine_version DbInstance#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#final_snapshot_identifier DbInstance#final_snapshot_identifier}.
        :param iam_database_authentication_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#iam_database_authentication_enabled DbInstance#iam_database_authentication_enabled}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#identifier DbInstance#identifier}.
        :param identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#identifier_prefix DbInstance#identifier_prefix}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#iops DbInstance#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#kms_key_id DbInstance#kms_key_id}.
        :param license_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#license_model DbInstance#license_model}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#maintenance_window DbInstance#maintenance_window}.
        :param max_allocated_storage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#max_allocated_storage DbInstance#max_allocated_storage}.
        :param monitoring_interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#monitoring_interval DbInstance#monitoring_interval}.
        :param monitoring_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#monitoring_role_arn DbInstance#monitoring_role_arn}.
        :param multi_az: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#multi_az DbInstance#multi_az}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#name DbInstance#name}.
        :param nchar_character_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#nchar_character_set_name DbInstance#nchar_character_set_name}.
        :param option_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#option_group_name DbInstance#option_group_name}.
        :param parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#parameter_group_name DbInstance#parameter_group_name}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#password DbInstance#password}.
        :param performance_insights_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#performance_insights_enabled DbInstance#performance_insights_enabled}.
        :param performance_insights_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#performance_insights_kms_key_id DbInstance#performance_insights_kms_key_id}.
        :param performance_insights_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#performance_insights_retention_period DbInstance#performance_insights_retention_period}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#port DbInstance#port}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#publicly_accessible DbInstance#publicly_accessible}.
        :param replica_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#replica_mode DbInstance#replica_mode}.
        :param replicate_source_db: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#replicate_source_db DbInstance#replicate_source_db}.
        :param restore_to_point_in_time: restore_to_point_in_time block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#restore_to_point_in_time DbInstance#restore_to_point_in_time}
        :param s3_import: s3_import block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#s3_import DbInstance#s3_import}
        :param security_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#security_group_names DbInstance#security_group_names}.
        :param skip_final_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#skip_final_snapshot DbInstance#skip_final_snapshot}.
        :param snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#snapshot_identifier DbInstance#snapshot_identifier}.
        :param storage_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#storage_encrypted DbInstance#storage_encrypted}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#storage_type DbInstance#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#tags DbInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#tags_all DbInstance#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#timeouts DbInstance#timeouts}
        :param timezone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#timezone DbInstance#timezone}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#username DbInstance#username}.
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#vpc_security_group_ids DbInstance#vpc_security_group_ids}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbInstanceConfig(
            instance_class=instance_class,
            allocated_storage=allocated_storage,
            allow_major_version_upgrade=allow_major_version_upgrade,
            apply_immediately=apply_immediately,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            availability_zone=availability_zone,
            backup_retention_period=backup_retention_period,
            backup_window=backup_window,
            ca_cert_identifier=ca_cert_identifier,
            character_set_name=character_set_name,
            copy_tags_to_snapshot=copy_tags_to_snapshot,
            customer_owned_ip_enabled=customer_owned_ip_enabled,
            db_subnet_group_name=db_subnet_group_name,
            delete_automated_backups=delete_automated_backups,
            deletion_protection=deletion_protection,
            domain=domain,
            domain_iam_role_name=domain_iam_role_name,
            enabled_cloudwatch_logs_exports=enabled_cloudwatch_logs_exports,
            engine=engine,
            engine_version=engine_version,
            final_snapshot_identifier=final_snapshot_identifier,
            iam_database_authentication_enabled=iam_database_authentication_enabled,
            identifier=identifier,
            identifier_prefix=identifier_prefix,
            iops=iops,
            kms_key_id=kms_key_id,
            license_model=license_model,
            maintenance_window=maintenance_window,
            max_allocated_storage=max_allocated_storage,
            monitoring_interval=monitoring_interval,
            monitoring_role_arn=monitoring_role_arn,
            multi_az=multi_az,
            name=name,
            nchar_character_set_name=nchar_character_set_name,
            option_group_name=option_group_name,
            parameter_group_name=parameter_group_name,
            password=password,
            performance_insights_enabled=performance_insights_enabled,
            performance_insights_kms_key_id=performance_insights_kms_key_id,
            performance_insights_retention_period=performance_insights_retention_period,
            port=port,
            publicly_accessible=publicly_accessible,
            replica_mode=replica_mode,
            replicate_source_db=replicate_source_db,
            restore_to_point_in_time=restore_to_point_in_time,
            s3_import=s3_import,
            security_group_names=security_group_names,
            skip_final_snapshot=skip_final_snapshot,
            snapshot_identifier=snapshot_identifier,
            storage_encrypted=storage_encrypted,
            storage_type=storage_type,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            timezone=timezone,
            username=username,
            vpc_security_group_ids=vpc_security_group_ids,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putRestoreToPointInTime")
    def put_restore_to_point_in_time(
        self,
        *,
        restore_time: typing.Optional[builtins.str] = None,
        source_db_instance_identifier: typing.Optional[builtins.str] = None,
        source_dbi_resource_id: typing.Optional[builtins.str] = None,
        use_latest_restorable_time: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param restore_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#restore_time DbInstance#restore_time}.
        :param source_db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_db_instance_identifier DbInstance#source_db_instance_identifier}.
        :param source_dbi_resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_dbi_resource_id DbInstance#source_dbi_resource_id}.
        :param use_latest_restorable_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#use_latest_restorable_time DbInstance#use_latest_restorable_time}.
        '''
        value = DbInstanceRestoreToPointInTime(
            restore_time=restore_time,
            source_db_instance_identifier=source_db_instance_identifier,
            source_dbi_resource_id=source_dbi_resource_id,
            use_latest_restorable_time=use_latest_restorable_time,
        )

        return typing.cast(None, jsii.invoke(self, "putRestoreToPointInTime", [value]))

    @jsii.member(jsii_name="putS3Import")
    def put_s3_import(
        self,
        *,
        bucket_name: builtins.str,
        ingestion_role: builtins.str,
        source_engine: builtins.str,
        source_engine_version: builtins.str,
        bucket_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#bucket_name DbInstance#bucket_name}.
        :param ingestion_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#ingestion_role DbInstance#ingestion_role}.
        :param source_engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_engine DbInstance#source_engine}.
        :param source_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_engine_version DbInstance#source_engine_version}.
        :param bucket_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#bucket_prefix DbInstance#bucket_prefix}.
        '''
        value = DbInstanceS3Import(
            bucket_name=bucket_name,
            ingestion_role=ingestion_role,
            source_engine=source_engine,
            source_engine_version=source_engine_version,
            bucket_prefix=bucket_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putS3Import", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#create DbInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#delete DbInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#update DbInstance#update}.
        '''
        value = DbInstanceTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAllocatedStorage")
    def reset_allocated_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllocatedStorage", []))

    @jsii.member(jsii_name="resetAllowMajorVersionUpgrade")
    def reset_allow_major_version_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowMajorVersionUpgrade", []))

    @jsii.member(jsii_name="resetApplyImmediately")
    def reset_apply_immediately(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyImmediately", []))

    @jsii.member(jsii_name="resetAutoMinorVersionUpgrade")
    def reset_auto_minor_version_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoMinorVersionUpgrade", []))

    @jsii.member(jsii_name="resetAvailabilityZone")
    def reset_availability_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZone", []))

    @jsii.member(jsii_name="resetBackupRetentionPeriod")
    def reset_backup_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupRetentionPeriod", []))

    @jsii.member(jsii_name="resetBackupWindow")
    def reset_backup_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupWindow", []))

    @jsii.member(jsii_name="resetCaCertIdentifier")
    def reset_ca_cert_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaCertIdentifier", []))

    @jsii.member(jsii_name="resetCharacterSetName")
    def reset_character_set_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCharacterSetName", []))

    @jsii.member(jsii_name="resetCopyTagsToSnapshot")
    def reset_copy_tags_to_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToSnapshot", []))

    @jsii.member(jsii_name="resetCustomerOwnedIpEnabled")
    def reset_customer_owned_ip_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomerOwnedIpEnabled", []))

    @jsii.member(jsii_name="resetDbSubnetGroupName")
    def reset_db_subnet_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbSubnetGroupName", []))

    @jsii.member(jsii_name="resetDeleteAutomatedBackups")
    def reset_delete_automated_backups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteAutomatedBackups", []))

    @jsii.member(jsii_name="resetDeletionProtection")
    def reset_deletion_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletionProtection", []))

    @jsii.member(jsii_name="resetDomain")
    def reset_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomain", []))

    @jsii.member(jsii_name="resetDomainIamRoleName")
    def reset_domain_iam_role_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainIamRoleName", []))

    @jsii.member(jsii_name="resetEnabledCloudwatchLogsExports")
    def reset_enabled_cloudwatch_logs_exports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabledCloudwatchLogsExports", []))

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

    @jsii.member(jsii_name="resetIdentifier")
    def reset_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentifier", []))

    @jsii.member(jsii_name="resetIdentifierPrefix")
    def reset_identifier_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentifierPrefix", []))

    @jsii.member(jsii_name="resetIops")
    def reset_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIops", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetLicenseModel")
    def reset_license_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLicenseModel", []))

    @jsii.member(jsii_name="resetMaintenanceWindow")
    def reset_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindow", []))

    @jsii.member(jsii_name="resetMaxAllocatedStorage")
    def reset_max_allocated_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAllocatedStorage", []))

    @jsii.member(jsii_name="resetMonitoringInterval")
    def reset_monitoring_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMonitoringInterval", []))

    @jsii.member(jsii_name="resetMonitoringRoleArn")
    def reset_monitoring_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMonitoringRoleArn", []))

    @jsii.member(jsii_name="resetMultiAz")
    def reset_multi_az(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultiAz", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNcharCharacterSetName")
    def reset_nchar_character_set_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNcharCharacterSetName", []))

    @jsii.member(jsii_name="resetOptionGroupName")
    def reset_option_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptionGroupName", []))

    @jsii.member(jsii_name="resetParameterGroupName")
    def reset_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterGroupName", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPerformanceInsightsEnabled")
    def reset_performance_insights_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerformanceInsightsEnabled", []))

    @jsii.member(jsii_name="resetPerformanceInsightsKmsKeyId")
    def reset_performance_insights_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerformanceInsightsKmsKeyId", []))

    @jsii.member(jsii_name="resetPerformanceInsightsRetentionPeriod")
    def reset_performance_insights_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerformanceInsightsRetentionPeriod", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetPubliclyAccessible")
    def reset_publicly_accessible(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPubliclyAccessible", []))

    @jsii.member(jsii_name="resetReplicaMode")
    def reset_replica_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicaMode", []))

    @jsii.member(jsii_name="resetReplicateSourceDb")
    def reset_replicate_source_db(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicateSourceDb", []))

    @jsii.member(jsii_name="resetRestoreToPointInTime")
    def reset_restore_to_point_in_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreToPointInTime", []))

    @jsii.member(jsii_name="resetS3Import")
    def reset_s3_import(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Import", []))

    @jsii.member(jsii_name="resetSecurityGroupNames")
    def reset_security_group_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupNames", []))

    @jsii.member(jsii_name="resetSkipFinalSnapshot")
    def reset_skip_final_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipFinalSnapshot", []))

    @jsii.member(jsii_name="resetSnapshotIdentifier")
    def reset_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetStorageEncrypted")
    def reset_storage_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageEncrypted", []))

    @jsii.member(jsii_name="resetStorageType")
    def reset_storage_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageType", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTimezone")
    def reset_timezone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimezone", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

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
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionActual")
    def engine_version_actual(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersionActual"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latestRestorableTime")
    def latest_restorable_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latestRestorableTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicas")
    def replicas(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "replicas"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreToPointInTime")
    def restore_to_point_in_time(
        self,
    ) -> "DbInstanceRestoreToPointInTimeOutputReference":
        return typing.cast("DbInstanceRestoreToPointInTimeOutputReference", jsii.get(self, "restoreToPointInTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Import")
    def s3_import(self) -> "DbInstanceS3ImportOutputReference":
        return typing.cast("DbInstanceS3ImportOutputReference", jsii.get(self, "s3Import"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DbInstanceTimeoutsOutputReference":
        return typing.cast("DbInstanceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocatedStorageInput")
    def allocated_storage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allocatedStorageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMajorVersionUpgradeInput")
    def allow_major_version_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowMajorVersionUpgradeInput"))

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
    @jsii.member(jsii_name="backupRetentionPeriodInput")
    def backup_retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupRetentionPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupWindowInput")
    def backup_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caCertIdentifierInput")
    def ca_cert_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="characterSetNameInput")
    def character_set_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "characterSetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToSnapshotInput")
    def copy_tags_to_snapshot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToSnapshotInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerOwnedIpEnabledInput")
    def customer_owned_ip_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "customerOwnedIpEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupNameInput")
    def db_subnet_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbSubnetGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAutomatedBackupsInput")
    def delete_automated_backups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deleteAutomatedBackupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deletionProtectionInput")
    def deletion_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deletionProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainIamRoleNameInput")
    def domain_iam_role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainIamRoleNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledCloudwatchLogsExportsInput")
    def enabled_cloudwatch_logs_exports_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "enabledCloudwatchLogsExportsInput"))

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
    @jsii.member(jsii_name="iopsInput")
    def iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iopsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseModelInput")
    def license_model_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "licenseModelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAllocatedStorageInput")
    def max_allocated_storage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAllocatedStorageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitoringIntervalInput")
    def monitoring_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "monitoringIntervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitoringRoleArnInput")
    def monitoring_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "monitoringRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAzInput")
    def multi_az_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "multiAzInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ncharCharacterSetNameInput")
    def nchar_character_set_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ncharCharacterSetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionGroupNameInput")
    def option_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "optionGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupNameInput")
    def parameter_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsEnabledInput")
    def performance_insights_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "performanceInsightsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsKmsKeyIdInput")
    def performance_insights_kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "performanceInsightsKmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsRetentionPeriodInput")
    def performance_insights_retention_period_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "performanceInsightsRetentionPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publiclyAccessibleInput")
    def publicly_accessible_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publiclyAccessibleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaModeInput")
    def replica_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicaModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicateSourceDbInput")
    def replicate_source_db_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicateSourceDbInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreToPointInTimeInput")
    def restore_to_point_in_time_input(
        self,
    ) -> typing.Optional["DbInstanceRestoreToPointInTime"]:
        return typing.cast(typing.Optional["DbInstanceRestoreToPointInTime"], jsii.get(self, "restoreToPointInTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ImportInput")
    def s3_import_input(self) -> typing.Optional["DbInstanceS3Import"]:
        return typing.cast(typing.Optional["DbInstanceS3Import"], jsii.get(self, "s3ImportInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupNamesInput")
    def security_group_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupNamesInput"))

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
    @jsii.member(jsii_name="storageTypeInput")
    def storage_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTypeInput"))

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
    def timeouts_input(self) -> typing.Optional["DbInstanceTimeouts"]:
        return typing.cast(typing.Optional["DbInstanceTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timezoneInput")
    def timezone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timezoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIdsInput")
    def vpc_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocatedStorage")
    def allocated_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "allocatedStorage"))

    @allocated_storage.setter
    def allocated_storage(self, value: jsii.Number) -> None:
        jsii.set(self, "allocatedStorage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMajorVersionUpgrade")
    def allow_major_version_upgrade(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowMajorVersionUpgrade"))

    @allow_major_version_upgrade.setter
    def allow_major_version_upgrade(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowMajorVersionUpgrade", value)

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
    @jsii.member(jsii_name="backupRetentionPeriod")
    def backup_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupRetentionPeriod"))

    @backup_retention_period.setter
    def backup_retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "backupRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backupWindow")
    def backup_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupWindow"))

    @backup_window.setter
    def backup_window(self, value: builtins.str) -> None:
        jsii.set(self, "backupWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caCertIdentifier")
    def ca_cert_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCertIdentifier"))

    @ca_cert_identifier.setter
    def ca_cert_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "caCertIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="characterSetName")
    def character_set_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "characterSetName"))

    @character_set_name.setter
    def character_set_name(self, value: builtins.str) -> None:
        jsii.set(self, "characterSetName", value)

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
    @jsii.member(jsii_name="customerOwnedIpEnabled")
    def customer_owned_ip_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "customerOwnedIpEnabled"))

    @customer_owned_ip_enabled.setter
    def customer_owned_ip_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "customerOwnedIpEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbSubnetGroupName"))

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbSubnetGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteAutomatedBackups")
    def delete_automated_backups(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deleteAutomatedBackups"))

    @delete_automated_backups.setter
    def delete_automated_backups(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "deleteAutomatedBackups", value)

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
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainIamRoleName")
    def domain_iam_role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainIamRoleName"))

    @domain_iam_role_name.setter
    def domain_iam_role_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainIamRoleName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledCloudwatchLogsExports")
    def enabled_cloudwatch_logs_exports(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "enabledCloudwatchLogsExports"))

    @enabled_cloudwatch_logs_exports.setter
    def enabled_cloudwatch_logs_exports(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "enabledCloudwatchLogsExports", value)

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
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @iops.setter
    def iops(self, value: jsii.Number) -> None:
        jsii.set(self, "iops", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseModel")
    def license_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseModel"))

    @license_model.setter
    def license_model(self, value: builtins.str) -> None:
        jsii.set(self, "licenseModel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindow"))

    @maintenance_window.setter
    def maintenance_window(self, value: builtins.str) -> None:
        jsii.set(self, "maintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAllocatedStorage")
    def max_allocated_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAllocatedStorage"))

    @max_allocated_storage.setter
    def max_allocated_storage(self, value: jsii.Number) -> None:
        jsii.set(self, "maxAllocatedStorage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitoringInterval")
    def monitoring_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "monitoringInterval"))

    @monitoring_interval.setter
    def monitoring_interval(self, value: jsii.Number) -> None:
        jsii.set(self, "monitoringInterval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitoringRoleArn")
    def monitoring_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitoringRoleArn"))

    @monitoring_role_arn.setter
    def monitoring_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "monitoringRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAz")
    def multi_az(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "multiAz"))

    @multi_az.setter
    def multi_az(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "multiAz", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ncharCharacterSetName")
    def nchar_character_set_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ncharCharacterSetName"))

    @nchar_character_set_name.setter
    def nchar_character_set_name(self, value: builtins.str) -> None:
        jsii.set(self, "ncharCharacterSetName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionGroupName")
    def option_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "optionGroupName"))

    @option_group_name.setter
    def option_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "optionGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupName"))

    @parameter_group_name.setter
    def parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "parameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsEnabled")
    def performance_insights_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "performanceInsightsEnabled"))

    @performance_insights_enabled.setter
    def performance_insights_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "performanceInsightsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsKmsKeyId")
    def performance_insights_kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "performanceInsightsKmsKeyId"))

    @performance_insights_kms_key_id.setter
    def performance_insights_kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "performanceInsightsKmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsRetentionPeriod")
    def performance_insights_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "performanceInsightsRetentionPeriod"))

    @performance_insights_retention_period.setter
    def performance_insights_retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "performanceInsightsRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

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
    @jsii.member(jsii_name="replicaMode")
    def replica_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicaMode"))

    @replica_mode.setter
    def replica_mode(self, value: builtins.str) -> None:
        jsii.set(self, "replicaMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicateSourceDb")
    def replicate_source_db(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicateSourceDb"))

    @replicate_source_db.setter
    def replicate_source_db(self, value: builtins.str) -> None:
        jsii.set(self, "replicateSourceDb", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupNames")
    def security_group_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupNames"))

    @security_group_names.setter
    def security_group_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupNames", value)

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
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @storage_type.setter
    def storage_type(self, value: builtins.str) -> None:
        jsii.set(self, "storageType", value)

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
    @jsii.member(jsii_name="timezone")
    def timezone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezone"))

    @timezone.setter
    def timezone(self, value: builtins.str) -> None:
        jsii.set(self, "timezone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSecurityGroupIds"))

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "vpcSecurityGroupIds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "instance_class": "instanceClass",
        "allocated_storage": "allocatedStorage",
        "allow_major_version_upgrade": "allowMajorVersionUpgrade",
        "apply_immediately": "applyImmediately",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "availability_zone": "availabilityZone",
        "backup_retention_period": "backupRetentionPeriod",
        "backup_window": "backupWindow",
        "ca_cert_identifier": "caCertIdentifier",
        "character_set_name": "characterSetName",
        "copy_tags_to_snapshot": "copyTagsToSnapshot",
        "customer_owned_ip_enabled": "customerOwnedIpEnabled",
        "db_subnet_group_name": "dbSubnetGroupName",
        "delete_automated_backups": "deleteAutomatedBackups",
        "deletion_protection": "deletionProtection",
        "domain": "domain",
        "domain_iam_role_name": "domainIamRoleName",
        "enabled_cloudwatch_logs_exports": "enabledCloudwatchLogsExports",
        "engine": "engine",
        "engine_version": "engineVersion",
        "final_snapshot_identifier": "finalSnapshotIdentifier",
        "iam_database_authentication_enabled": "iamDatabaseAuthenticationEnabled",
        "identifier": "identifier",
        "identifier_prefix": "identifierPrefix",
        "iops": "iops",
        "kms_key_id": "kmsKeyId",
        "license_model": "licenseModel",
        "maintenance_window": "maintenanceWindow",
        "max_allocated_storage": "maxAllocatedStorage",
        "monitoring_interval": "monitoringInterval",
        "monitoring_role_arn": "monitoringRoleArn",
        "multi_az": "multiAz",
        "name": "name",
        "nchar_character_set_name": "ncharCharacterSetName",
        "option_group_name": "optionGroupName",
        "parameter_group_name": "parameterGroupName",
        "password": "password",
        "performance_insights_enabled": "performanceInsightsEnabled",
        "performance_insights_kms_key_id": "performanceInsightsKmsKeyId",
        "performance_insights_retention_period": "performanceInsightsRetentionPeriod",
        "port": "port",
        "publicly_accessible": "publiclyAccessible",
        "replica_mode": "replicaMode",
        "replicate_source_db": "replicateSourceDb",
        "restore_to_point_in_time": "restoreToPointInTime",
        "s3_import": "s3Import",
        "security_group_names": "securityGroupNames",
        "skip_final_snapshot": "skipFinalSnapshot",
        "snapshot_identifier": "snapshotIdentifier",
        "storage_encrypted": "storageEncrypted",
        "storage_type": "storageType",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "timezone": "timezone",
        "username": "username",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class DbInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        instance_class: builtins.str,
        allocated_storage: typing.Optional[jsii.Number] = None,
        allow_major_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        backup_retention_period: typing.Optional[jsii.Number] = None,
        backup_window: typing.Optional[builtins.str] = None,
        ca_cert_identifier: typing.Optional[builtins.str] = None,
        character_set_name: typing.Optional[builtins.str] = None,
        copy_tags_to_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        customer_owned_ip_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        delete_automated_backups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_iam_role_name: typing.Optional[builtins.str] = None,
        enabled_cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        iam_database_authentication_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        identifier: typing.Optional[builtins.str] = None,
        identifier_prefix: typing.Optional[builtins.str] = None,
        iops: typing.Optional[jsii.Number] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        license_model: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        max_allocated_storage: typing.Optional[jsii.Number] = None,
        monitoring_interval: typing.Optional[jsii.Number] = None,
        monitoring_role_arn: typing.Optional[builtins.str] = None,
        multi_az: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        nchar_character_set_name: typing.Optional[builtins.str] = None,
        option_group_name: typing.Optional[builtins.str] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        performance_insights_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        performance_insights_kms_key_id: typing.Optional[builtins.str] = None,
        performance_insights_retention_period: typing.Optional[jsii.Number] = None,
        port: typing.Optional[jsii.Number] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        replica_mode: typing.Optional[builtins.str] = None,
        replicate_source_db: typing.Optional[builtins.str] = None,
        restore_to_point_in_time: typing.Optional["DbInstanceRestoreToPointInTime"] = None,
        s3_import: typing.Optional["DbInstanceS3Import"] = None,
        security_group_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        skip_final_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        storage_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbInstanceTimeouts"] = None,
        timezone: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#instance_class DbInstance#instance_class}.
        :param allocated_storage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#allocated_storage DbInstance#allocated_storage}.
        :param allow_major_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#allow_major_version_upgrade DbInstance#allow_major_version_upgrade}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#apply_immediately DbInstance#apply_immediately}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#auto_minor_version_upgrade DbInstance#auto_minor_version_upgrade}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#availability_zone DbInstance#availability_zone}.
        :param backup_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#backup_retention_period DbInstance#backup_retention_period}.
        :param backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#backup_window DbInstance#backup_window}.
        :param ca_cert_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#ca_cert_identifier DbInstance#ca_cert_identifier}.
        :param character_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#character_set_name DbInstance#character_set_name}.
        :param copy_tags_to_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#copy_tags_to_snapshot DbInstance#copy_tags_to_snapshot}.
        :param customer_owned_ip_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#customer_owned_ip_enabled DbInstance#customer_owned_ip_enabled}.
        :param db_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#db_subnet_group_name DbInstance#db_subnet_group_name}.
        :param delete_automated_backups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#delete_automated_backups DbInstance#delete_automated_backups}.
        :param deletion_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#deletion_protection DbInstance#deletion_protection}.
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#domain DbInstance#domain}.
        :param domain_iam_role_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#domain_iam_role_name DbInstance#domain_iam_role_name}.
        :param enabled_cloudwatch_logs_exports: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#enabled_cloudwatch_logs_exports DbInstance#enabled_cloudwatch_logs_exports}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#engine DbInstance#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#engine_version DbInstance#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#final_snapshot_identifier DbInstance#final_snapshot_identifier}.
        :param iam_database_authentication_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#iam_database_authentication_enabled DbInstance#iam_database_authentication_enabled}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#identifier DbInstance#identifier}.
        :param identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#identifier_prefix DbInstance#identifier_prefix}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#iops DbInstance#iops}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#kms_key_id DbInstance#kms_key_id}.
        :param license_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#license_model DbInstance#license_model}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#maintenance_window DbInstance#maintenance_window}.
        :param max_allocated_storage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#max_allocated_storage DbInstance#max_allocated_storage}.
        :param monitoring_interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#monitoring_interval DbInstance#monitoring_interval}.
        :param monitoring_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#monitoring_role_arn DbInstance#monitoring_role_arn}.
        :param multi_az: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#multi_az DbInstance#multi_az}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#name DbInstance#name}.
        :param nchar_character_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#nchar_character_set_name DbInstance#nchar_character_set_name}.
        :param option_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#option_group_name DbInstance#option_group_name}.
        :param parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#parameter_group_name DbInstance#parameter_group_name}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#password DbInstance#password}.
        :param performance_insights_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#performance_insights_enabled DbInstance#performance_insights_enabled}.
        :param performance_insights_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#performance_insights_kms_key_id DbInstance#performance_insights_kms_key_id}.
        :param performance_insights_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#performance_insights_retention_period DbInstance#performance_insights_retention_period}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#port DbInstance#port}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#publicly_accessible DbInstance#publicly_accessible}.
        :param replica_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#replica_mode DbInstance#replica_mode}.
        :param replicate_source_db: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#replicate_source_db DbInstance#replicate_source_db}.
        :param restore_to_point_in_time: restore_to_point_in_time block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#restore_to_point_in_time DbInstance#restore_to_point_in_time}
        :param s3_import: s3_import block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#s3_import DbInstance#s3_import}
        :param security_group_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#security_group_names DbInstance#security_group_names}.
        :param skip_final_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#skip_final_snapshot DbInstance#skip_final_snapshot}.
        :param snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#snapshot_identifier DbInstance#snapshot_identifier}.
        :param storage_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#storage_encrypted DbInstance#storage_encrypted}.
        :param storage_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#storage_type DbInstance#storage_type}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#tags DbInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#tags_all DbInstance#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#timeouts DbInstance#timeouts}
        :param timezone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#timezone DbInstance#timezone}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#username DbInstance#username}.
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#vpc_security_group_ids DbInstance#vpc_security_group_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(restore_to_point_in_time, dict):
            restore_to_point_in_time = DbInstanceRestoreToPointInTime(**restore_to_point_in_time)
        if isinstance(s3_import, dict):
            s3_import = DbInstanceS3Import(**s3_import)
        if isinstance(timeouts, dict):
            timeouts = DbInstanceTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
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
        if allocated_storage is not None:
            self._values["allocated_storage"] = allocated_storage
        if allow_major_version_upgrade is not None:
            self._values["allow_major_version_upgrade"] = allow_major_version_upgrade
        if apply_immediately is not None:
            self._values["apply_immediately"] = apply_immediately
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if backup_retention_period is not None:
            self._values["backup_retention_period"] = backup_retention_period
        if backup_window is not None:
            self._values["backup_window"] = backup_window
        if ca_cert_identifier is not None:
            self._values["ca_cert_identifier"] = ca_cert_identifier
        if character_set_name is not None:
            self._values["character_set_name"] = character_set_name
        if copy_tags_to_snapshot is not None:
            self._values["copy_tags_to_snapshot"] = copy_tags_to_snapshot
        if customer_owned_ip_enabled is not None:
            self._values["customer_owned_ip_enabled"] = customer_owned_ip_enabled
        if db_subnet_group_name is not None:
            self._values["db_subnet_group_name"] = db_subnet_group_name
        if delete_automated_backups is not None:
            self._values["delete_automated_backups"] = delete_automated_backups
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if domain is not None:
            self._values["domain"] = domain
        if domain_iam_role_name is not None:
            self._values["domain_iam_role_name"] = domain_iam_role_name
        if enabled_cloudwatch_logs_exports is not None:
            self._values["enabled_cloudwatch_logs_exports"] = enabled_cloudwatch_logs_exports
        if engine is not None:
            self._values["engine"] = engine
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if final_snapshot_identifier is not None:
            self._values["final_snapshot_identifier"] = final_snapshot_identifier
        if iam_database_authentication_enabled is not None:
            self._values["iam_database_authentication_enabled"] = iam_database_authentication_enabled
        if identifier is not None:
            self._values["identifier"] = identifier
        if identifier_prefix is not None:
            self._values["identifier_prefix"] = identifier_prefix
        if iops is not None:
            self._values["iops"] = iops
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if license_model is not None:
            self._values["license_model"] = license_model
        if maintenance_window is not None:
            self._values["maintenance_window"] = maintenance_window
        if max_allocated_storage is not None:
            self._values["max_allocated_storage"] = max_allocated_storage
        if monitoring_interval is not None:
            self._values["monitoring_interval"] = monitoring_interval
        if monitoring_role_arn is not None:
            self._values["monitoring_role_arn"] = monitoring_role_arn
        if multi_az is not None:
            self._values["multi_az"] = multi_az
        if name is not None:
            self._values["name"] = name
        if nchar_character_set_name is not None:
            self._values["nchar_character_set_name"] = nchar_character_set_name
        if option_group_name is not None:
            self._values["option_group_name"] = option_group_name
        if parameter_group_name is not None:
            self._values["parameter_group_name"] = parameter_group_name
        if password is not None:
            self._values["password"] = password
        if performance_insights_enabled is not None:
            self._values["performance_insights_enabled"] = performance_insights_enabled
        if performance_insights_kms_key_id is not None:
            self._values["performance_insights_kms_key_id"] = performance_insights_kms_key_id
        if performance_insights_retention_period is not None:
            self._values["performance_insights_retention_period"] = performance_insights_retention_period
        if port is not None:
            self._values["port"] = port
        if publicly_accessible is not None:
            self._values["publicly_accessible"] = publicly_accessible
        if replica_mode is not None:
            self._values["replica_mode"] = replica_mode
        if replicate_source_db is not None:
            self._values["replicate_source_db"] = replicate_source_db
        if restore_to_point_in_time is not None:
            self._values["restore_to_point_in_time"] = restore_to_point_in_time
        if s3_import is not None:
            self._values["s3_import"] = s3_import
        if security_group_names is not None:
            self._values["security_group_names"] = security_group_names
        if skip_final_snapshot is not None:
            self._values["skip_final_snapshot"] = skip_final_snapshot
        if snapshot_identifier is not None:
            self._values["snapshot_identifier"] = snapshot_identifier
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if storage_type is not None:
            self._values["storage_type"] = storage_type
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if timezone is not None:
            self._values["timezone"] = timezone
        if username is not None:
            self._values["username"] = username
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
    def instance_class(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#instance_class DbInstance#instance_class}.'''
        result = self._values.get("instance_class")
        assert result is not None, "Required property 'instance_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocated_storage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#allocated_storage DbInstance#allocated_storage}.'''
        result = self._values.get("allocated_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allow_major_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#allow_major_version_upgrade DbInstance#allow_major_version_upgrade}.'''
        result = self._values.get("allow_major_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def apply_immediately(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#apply_immediately DbInstance#apply_immediately}.'''
        result = self._values.get("apply_immediately")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#auto_minor_version_upgrade DbInstance#auto_minor_version_upgrade}.'''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#availability_zone DbInstance#availability_zone}.'''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#backup_retention_period DbInstance#backup_retention_period}.'''
        result = self._values.get("backup_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#backup_window DbInstance#backup_window}.'''
        result = self._values.get("backup_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_cert_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#ca_cert_identifier DbInstance#ca_cert_identifier}.'''
        result = self._values.get("ca_cert_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def character_set_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#character_set_name DbInstance#character_set_name}.'''
        result = self._values.get("character_set_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_tags_to_snapshot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#copy_tags_to_snapshot DbInstance#copy_tags_to_snapshot}.'''
        result = self._values.get("copy_tags_to_snapshot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def customer_owned_ip_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#customer_owned_ip_enabled DbInstance#customer_owned_ip_enabled}.'''
        result = self._values.get("customer_owned_ip_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def db_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#db_subnet_group_name DbInstance#db_subnet_group_name}.'''
        result = self._values.get("db_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_automated_backups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#delete_automated_backups DbInstance#delete_automated_backups}.'''
        result = self._values.get("delete_automated_backups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def deletion_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#deletion_protection DbInstance#deletion_protection}.'''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#domain DbInstance#domain}.'''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_iam_role_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#domain_iam_role_name DbInstance#domain_iam_role_name}.'''
        result = self._values.get("domain_iam_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled_cloudwatch_logs_exports(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#enabled_cloudwatch_logs_exports DbInstance#enabled_cloudwatch_logs_exports}.'''
        result = self._values.get("enabled_cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#engine DbInstance#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#engine_version DbInstance#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#final_snapshot_identifier DbInstance#final_snapshot_identifier}.'''
        result = self._values.get("final_snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_database_authentication_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#iam_database_authentication_enabled DbInstance#iam_database_authentication_enabled}.'''
        result = self._values.get("iam_database_authentication_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#identifier DbInstance#identifier}.'''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identifier_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#identifier_prefix DbInstance#identifier_prefix}.'''
        result = self._values.get("identifier_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#iops DbInstance#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#kms_key_id DbInstance#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def license_model(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#license_model DbInstance#license_model}.'''
        result = self._values.get("license_model")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#maintenance_window DbInstance#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_allocated_storage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#max_allocated_storage DbInstance#max_allocated_storage}.'''
        result = self._values.get("max_allocated_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def monitoring_interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#monitoring_interval DbInstance#monitoring_interval}.'''
        result = self._values.get("monitoring_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def monitoring_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#monitoring_role_arn DbInstance#monitoring_role_arn}.'''
        result = self._values.get("monitoring_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def multi_az(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#multi_az DbInstance#multi_az}.'''
        result = self._values.get("multi_az")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#name DbInstance#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nchar_character_set_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#nchar_character_set_name DbInstance#nchar_character_set_name}.'''
        result = self._values.get("nchar_character_set_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def option_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#option_group_name DbInstance#option_group_name}.'''
        result = self._values.get("option_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#parameter_group_name DbInstance#parameter_group_name}.'''
        result = self._values.get("parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#password DbInstance#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def performance_insights_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#performance_insights_enabled DbInstance#performance_insights_enabled}.'''
        result = self._values.get("performance_insights_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def performance_insights_kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#performance_insights_kms_key_id DbInstance#performance_insights_kms_key_id}.'''
        result = self._values.get("performance_insights_kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def performance_insights_retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#performance_insights_retention_period DbInstance#performance_insights_retention_period}.'''
        result = self._values.get("performance_insights_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#port DbInstance#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def publicly_accessible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#publicly_accessible DbInstance#publicly_accessible}.'''
        result = self._values.get("publicly_accessible")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def replica_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#replica_mode DbInstance#replica_mode}.'''
        result = self._values.get("replica_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replicate_source_db(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#replicate_source_db DbInstance#replicate_source_db}.'''
        result = self._values.get("replicate_source_db")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restore_to_point_in_time(
        self,
    ) -> typing.Optional["DbInstanceRestoreToPointInTime"]:
        '''restore_to_point_in_time block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#restore_to_point_in_time DbInstance#restore_to_point_in_time}
        '''
        result = self._values.get("restore_to_point_in_time")
        return typing.cast(typing.Optional["DbInstanceRestoreToPointInTime"], result)

    @builtins.property
    def s3_import(self) -> typing.Optional["DbInstanceS3Import"]:
        '''s3_import block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#s3_import DbInstance#s3_import}
        '''
        result = self._values.get("s3_import")
        return typing.cast(typing.Optional["DbInstanceS3Import"], result)

    @builtins.property
    def security_group_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#security_group_names DbInstance#security_group_names}.'''
        result = self._values.get("security_group_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def skip_final_snapshot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#skip_final_snapshot DbInstance#skip_final_snapshot}.'''
        result = self._values.get("skip_final_snapshot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#snapshot_identifier DbInstance#snapshot_identifier}.'''
        result = self._values.get("snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#storage_encrypted DbInstance#storage_encrypted}.'''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#storage_type DbInstance#storage_type}.'''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#tags DbInstance#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#tags_all DbInstance#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DbInstanceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#timeouts DbInstance#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DbInstanceTimeouts"], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#timezone DbInstance#timezone}.'''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#username DbInstance#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#vpc_security_group_ids DbInstance#vpc_security_group_ids}.'''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbInstanceRestoreToPointInTime",
    jsii_struct_bases=[],
    name_mapping={
        "restore_time": "restoreTime",
        "source_db_instance_identifier": "sourceDbInstanceIdentifier",
        "source_dbi_resource_id": "sourceDbiResourceId",
        "use_latest_restorable_time": "useLatestRestorableTime",
    },
)
class DbInstanceRestoreToPointInTime:
    def __init__(
        self,
        *,
        restore_time: typing.Optional[builtins.str] = None,
        source_db_instance_identifier: typing.Optional[builtins.str] = None,
        source_dbi_resource_id: typing.Optional[builtins.str] = None,
        use_latest_restorable_time: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param restore_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#restore_time DbInstance#restore_time}.
        :param source_db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_db_instance_identifier DbInstance#source_db_instance_identifier}.
        :param source_dbi_resource_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_dbi_resource_id DbInstance#source_dbi_resource_id}.
        :param use_latest_restorable_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#use_latest_restorable_time DbInstance#use_latest_restorable_time}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if restore_time is not None:
            self._values["restore_time"] = restore_time
        if source_db_instance_identifier is not None:
            self._values["source_db_instance_identifier"] = source_db_instance_identifier
        if source_dbi_resource_id is not None:
            self._values["source_dbi_resource_id"] = source_dbi_resource_id
        if use_latest_restorable_time is not None:
            self._values["use_latest_restorable_time"] = use_latest_restorable_time

    @builtins.property
    def restore_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#restore_time DbInstance#restore_time}.'''
        result = self._values.get("restore_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_db_instance_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_db_instance_identifier DbInstance#source_db_instance_identifier}.'''
        result = self._values.get("source_db_instance_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_dbi_resource_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_dbi_resource_id DbInstance#source_dbi_resource_id}.'''
        result = self._values.get("source_dbi_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_latest_restorable_time(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#use_latest_restorable_time DbInstance#use_latest_restorable_time}.'''
        result = self._values.get("use_latest_restorable_time")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbInstanceRestoreToPointInTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbInstanceRestoreToPointInTimeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbInstanceRestoreToPointInTimeOutputReference",
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

    @jsii.member(jsii_name="resetRestoreTime")
    def reset_restore_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreTime", []))

    @jsii.member(jsii_name="resetSourceDbInstanceIdentifier")
    def reset_source_db_instance_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceDbInstanceIdentifier", []))

    @jsii.member(jsii_name="resetSourceDbiResourceId")
    def reset_source_dbi_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceDbiResourceId", []))

    @jsii.member(jsii_name="resetUseLatestRestorableTime")
    def reset_use_latest_restorable_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseLatestRestorableTime", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreTimeInput")
    def restore_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restoreTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDbInstanceIdentifierInput")
    def source_db_instance_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceDbInstanceIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDbiResourceIdInput")
    def source_dbi_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceDbiResourceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useLatestRestorableTimeInput")
    def use_latest_restorable_time_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useLatestRestorableTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreTime")
    def restore_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restoreTime"))

    @restore_time.setter
    def restore_time(self, value: builtins.str) -> None:
        jsii.set(self, "restoreTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDbInstanceIdentifier")
    def source_db_instance_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDbInstanceIdentifier"))

    @source_db_instance_identifier.setter
    def source_db_instance_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "sourceDbInstanceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDbiResourceId")
    def source_dbi_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDbiResourceId"))

    @source_dbi_resource_id.setter
    def source_dbi_resource_id(self, value: builtins.str) -> None:
        jsii.set(self, "sourceDbiResourceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useLatestRestorableTime")
    def use_latest_restorable_time(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useLatestRestorableTime"))

    @use_latest_restorable_time.setter
    def use_latest_restorable_time(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useLatestRestorableTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DbInstanceRestoreToPointInTime]:
        return typing.cast(typing.Optional[DbInstanceRestoreToPointInTime], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DbInstanceRestoreToPointInTime],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DbInstanceRoleAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbInstanceRoleAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association aws_db_instance_role_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_instance_identifier: builtins.str,
        feature_name: builtins.str,
        role_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association aws_db_instance_role_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association#db_instance_identifier DbInstanceRoleAssociation#db_instance_identifier}.
        :param feature_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association#feature_name DbInstanceRoleAssociation#feature_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association#role_arn DbInstanceRoleAssociation#role_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbInstanceRoleAssociationConfig(
            db_instance_identifier=db_instance_identifier,
            feature_name=feature_name,
            role_arn=role_arn,
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
    @jsii.member(jsii_name="dbInstanceIdentifierInput")
    def db_instance_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbInstanceIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureNameInput")
    def feature_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "featureNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceIdentifier"))

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbInstanceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureName")
    def feature_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "featureName"))

    @feature_name.setter
    def feature_name(self, value: builtins.str) -> None:
        jsii.set(self, "featureName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbInstanceRoleAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_instance_identifier": "dbInstanceIdentifier",
        "feature_name": "featureName",
        "role_arn": "roleArn",
    },
)
class DbInstanceRoleAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_instance_identifier: builtins.str,
        feature_name: builtins.str,
        role_arn: builtins.str,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association#db_instance_identifier DbInstanceRoleAssociation#db_instance_identifier}.
        :param feature_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association#feature_name DbInstanceRoleAssociation#feature_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association#role_arn DbInstanceRoleAssociation#role_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "db_instance_identifier": db_instance_identifier,
            "feature_name": feature_name,
            "role_arn": role_arn,
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
    def db_instance_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association#db_instance_identifier DbInstanceRoleAssociation#db_instance_identifier}.'''
        result = self._values.get("db_instance_identifier")
        assert result is not None, "Required property 'db_instance_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def feature_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association#feature_name DbInstanceRoleAssociation#feature_name}.'''
        result = self._values.get("feature_name")
        assert result is not None, "Required property 'feature_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance_role_association#role_arn DbInstanceRoleAssociation#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbInstanceRoleAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbInstanceS3Import",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "ingestion_role": "ingestionRole",
        "source_engine": "sourceEngine",
        "source_engine_version": "sourceEngineVersion",
        "bucket_prefix": "bucketPrefix",
    },
)
class DbInstanceS3Import:
    def __init__(
        self,
        *,
        bucket_name: builtins.str,
        ingestion_role: builtins.str,
        source_engine: builtins.str,
        source_engine_version: builtins.str,
        bucket_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#bucket_name DbInstance#bucket_name}.
        :param ingestion_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#ingestion_role DbInstance#ingestion_role}.
        :param source_engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_engine DbInstance#source_engine}.
        :param source_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_engine_version DbInstance#source_engine_version}.
        :param bucket_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#bucket_prefix DbInstance#bucket_prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
            "ingestion_role": ingestion_role,
            "source_engine": source_engine,
            "source_engine_version": source_engine_version,
        }
        if bucket_prefix is not None:
            self._values["bucket_prefix"] = bucket_prefix

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#bucket_name DbInstance#bucket_name}.'''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ingestion_role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#ingestion_role DbInstance#ingestion_role}.'''
        result = self._values.get("ingestion_role")
        assert result is not None, "Required property 'ingestion_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_engine(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_engine DbInstance#source_engine}.'''
        result = self._values.get("source_engine")
        assert result is not None, "Required property 'source_engine' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_engine_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#source_engine_version DbInstance#source_engine_version}.'''
        result = self._values.get("source_engine_version")
        assert result is not None, "Required property 'source_engine_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#bucket_prefix DbInstance#bucket_prefix}.'''
        result = self._values.get("bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbInstanceS3Import(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbInstanceS3ImportOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbInstanceS3ImportOutputReference",
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

    @jsii.member(jsii_name="resetBucketPrefix")
    def reset_bucket_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketPrefixInput")
    def bucket_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingestionRoleInput")
    def ingestion_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ingestionRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEngineInput")
    def source_engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceEngineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEngineVersionInput")
    def source_engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceEngineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "bucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketPrefix")
    def bucket_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketPrefix"))

    @bucket_prefix.setter
    def bucket_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "bucketPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingestionRole")
    def ingestion_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ingestionRole"))

    @ingestion_role.setter
    def ingestion_role(self, value: builtins.str) -> None:
        jsii.set(self, "ingestionRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEngine")
    def source_engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceEngine"))

    @source_engine.setter
    def source_engine(self, value: builtins.str) -> None:
        jsii.set(self, "sourceEngine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEngineVersion")
    def source_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceEngineVersion"))

    @source_engine_version.setter
    def source_engine_version(self, value: builtins.str) -> None:
        jsii.set(self, "sourceEngineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DbInstanceS3Import]:
        return typing.cast(typing.Optional[DbInstanceS3Import], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DbInstanceS3Import]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbInstanceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class DbInstanceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#create DbInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#delete DbInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#update DbInstance#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#create DbInstance#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#delete DbInstance#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_instance#update DbInstance#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbInstanceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbInstanceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbInstanceTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[DbInstanceTimeouts]:
        return typing.cast(typing.Optional[DbInstanceTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DbInstanceTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class DbOptionGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbOptionGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_option_group aws_db_option_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        engine_name: builtins.str,
        major_engine_version: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        option: typing.Optional[typing.Sequence["DbOptionGroupOption"]] = None,
        option_group_description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbOptionGroupTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_option_group aws_db_option_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param engine_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#engine_name DbOptionGroup#engine_name}.
        :param major_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#major_engine_version DbOptionGroup#major_engine_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#name DbOptionGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#name_prefix DbOptionGroup#name_prefix}.
        :param option: option block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option DbOptionGroup#option}
        :param option_group_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option_group_description DbOptionGroup#option_group_description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#tags DbOptionGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#tags_all DbOptionGroup#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#timeouts DbOptionGroup#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbOptionGroupConfig(
            engine_name=engine_name,
            major_engine_version=major_engine_version,
            name=name,
            name_prefix=name_prefix,
            option=option,
            option_group_description=option_group_description,
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
    def put_timeouts(self, *, delete: typing.Optional[builtins.str] = None) -> None:
        '''
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#delete DbOptionGroup#delete}.
        '''
        value = DbOptionGroupTimeouts(delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetOption")
    def reset_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOption", []))

    @jsii.member(jsii_name="resetOptionGroupDescription")
    def reset_option_group_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptionGroupDescription", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DbOptionGroupTimeoutsOutputReference":
        return typing.cast("DbOptionGroupTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineNameInput")
    def engine_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="majorEngineVersionInput")
    def major_engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "majorEngineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionGroupDescriptionInput")
    def option_group_description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "optionGroupDescriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionInput")
    def option_input(self) -> typing.Optional[typing.List["DbOptionGroupOption"]]:
        return typing.cast(typing.Optional[typing.List["DbOptionGroupOption"]], jsii.get(self, "optionInput"))

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
    def timeouts_input(self) -> typing.Optional["DbOptionGroupTimeouts"]:
        return typing.cast(typing.Optional["DbOptionGroupTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineName")
    def engine_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineName"))

    @engine_name.setter
    def engine_name(self, value: builtins.str) -> None:
        jsii.set(self, "engineName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="majorEngineVersion")
    def major_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "majorEngineVersion"))

    @major_engine_version.setter
    def major_engine_version(self, value: builtins.str) -> None:
        jsii.set(self, "majorEngineVersion", value)

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
    @jsii.member(jsii_name="option")
    def option(self) -> typing.List["DbOptionGroupOption"]:
        return typing.cast(typing.List["DbOptionGroupOption"], jsii.get(self, "option"))

    @option.setter
    def option(self, value: typing.List["DbOptionGroupOption"]) -> None:
        jsii.set(self, "option", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionGroupDescription")
    def option_group_description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "optionGroupDescription"))

    @option_group_description.setter
    def option_group_description(self, value: builtins.str) -> None:
        jsii.set(self, "optionGroupDescription", value)

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
    jsii_type="@cdktf/provider-aws.rds.DbOptionGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "engine_name": "engineName",
        "major_engine_version": "majorEngineVersion",
        "name": "name",
        "name_prefix": "namePrefix",
        "option": "option",
        "option_group_description": "optionGroupDescription",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class DbOptionGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        engine_name: builtins.str,
        major_engine_version: builtins.str,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        option: typing.Optional[typing.Sequence["DbOptionGroupOption"]] = None,
        option_group_description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbOptionGroupTimeouts"] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param engine_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#engine_name DbOptionGroup#engine_name}.
        :param major_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#major_engine_version DbOptionGroup#major_engine_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#name DbOptionGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#name_prefix DbOptionGroup#name_prefix}.
        :param option: option block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option DbOptionGroup#option}
        :param option_group_description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option_group_description DbOptionGroup#option_group_description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#tags DbOptionGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#tags_all DbOptionGroup#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#timeouts DbOptionGroup#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DbOptionGroupTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "engine_name": engine_name,
            "major_engine_version": major_engine_version,
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
        if option is not None:
            self._values["option"] = option
        if option_group_description is not None:
            self._values["option_group_description"] = option_group_description
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
    def engine_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#engine_name DbOptionGroup#engine_name}.'''
        result = self._values.get("engine_name")
        assert result is not None, "Required property 'engine_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def major_engine_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#major_engine_version DbOptionGroup#major_engine_version}.'''
        result = self._values.get("major_engine_version")
        assert result is not None, "Required property 'major_engine_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#name DbOptionGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#name_prefix DbOptionGroup#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def option(self) -> typing.Optional[typing.List["DbOptionGroupOption"]]:
        '''option block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option DbOptionGroup#option}
        '''
        result = self._values.get("option")
        return typing.cast(typing.Optional[typing.List["DbOptionGroupOption"]], result)

    @builtins.property
    def option_group_description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option_group_description DbOptionGroup#option_group_description}.'''
        result = self._values.get("option_group_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#tags DbOptionGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#tags_all DbOptionGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DbOptionGroupTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#timeouts DbOptionGroup#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DbOptionGroupTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbOptionGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbOptionGroupOption",
    jsii_struct_bases=[],
    name_mapping={
        "option_name": "optionName",
        "db_security_group_memberships": "dbSecurityGroupMemberships",
        "option_settings": "optionSettings",
        "port": "port",
        "version": "version",
        "vpc_security_group_memberships": "vpcSecurityGroupMemberships",
    },
)
class DbOptionGroupOption:
    def __init__(
        self,
        *,
        option_name: builtins.str,
        db_security_group_memberships: typing.Optional[typing.Sequence[builtins.str]] = None,
        option_settings: typing.Optional[typing.Sequence["DbOptionGroupOptionOptionSettings"]] = None,
        port: typing.Optional[jsii.Number] = None,
        version: typing.Optional[builtins.str] = None,
        vpc_security_group_memberships: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param option_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option_name DbOptionGroup#option_name}.
        :param db_security_group_memberships: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#db_security_group_memberships DbOptionGroup#db_security_group_memberships}.
        :param option_settings: option_settings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option_settings DbOptionGroup#option_settings}
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#port DbOptionGroup#port}.
        :param version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#version DbOptionGroup#version}.
        :param vpc_security_group_memberships: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#vpc_security_group_memberships DbOptionGroup#vpc_security_group_memberships}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "option_name": option_name,
        }
        if db_security_group_memberships is not None:
            self._values["db_security_group_memberships"] = db_security_group_memberships
        if option_settings is not None:
            self._values["option_settings"] = option_settings
        if port is not None:
            self._values["port"] = port
        if version is not None:
            self._values["version"] = version
        if vpc_security_group_memberships is not None:
            self._values["vpc_security_group_memberships"] = vpc_security_group_memberships

    @builtins.property
    def option_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option_name DbOptionGroup#option_name}.'''
        result = self._values.get("option_name")
        assert result is not None, "Required property 'option_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_security_group_memberships(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#db_security_group_memberships DbOptionGroup#db_security_group_memberships}.'''
        result = self._values.get("db_security_group_memberships")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def option_settings(
        self,
    ) -> typing.Optional[typing.List["DbOptionGroupOptionOptionSettings"]]:
        '''option_settings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#option_settings DbOptionGroup#option_settings}
        '''
        result = self._values.get("option_settings")
        return typing.cast(typing.Optional[typing.List["DbOptionGroupOptionOptionSettings"]], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#port DbOptionGroup#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#version DbOptionGroup#version}.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_security_group_memberships(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#vpc_security_group_memberships DbOptionGroup#vpc_security_group_memberships}.'''
        result = self._values.get("vpc_security_group_memberships")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbOptionGroupOption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbOptionGroupOptionOptionSettings",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class DbOptionGroupOptionOptionSettings:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#name DbOptionGroup#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#value DbOptionGroup#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#name DbOptionGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#value DbOptionGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbOptionGroupOptionOptionSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbOptionGroupTimeouts",
    jsii_struct_bases=[],
    name_mapping={"delete": "delete"},
)
class DbOptionGroupTimeouts:
    def __init__(self, *, delete: typing.Optional[builtins.str] = None) -> None:
        '''
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#delete DbOptionGroup#delete}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_option_group#delete DbOptionGroup#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbOptionGroupTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbOptionGroupTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbOptionGroupTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DbOptionGroupTimeouts]:
        return typing.cast(typing.Optional[DbOptionGroupTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DbOptionGroupTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class DbParameterGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbParameterGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group aws_db_parameter_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        family: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["DbParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group aws_db_parameter_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#family DbParameterGroup#family}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#description DbParameterGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#name DbParameterGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#name_prefix DbParameterGroup#name_prefix}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#parameter DbParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#tags DbParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#tags_all DbParameterGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbParameterGroupConfig(
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
    ) -> typing.Optional[typing.List["DbParameterGroupParameter"]]:
        return typing.cast(typing.Optional[typing.List["DbParameterGroupParameter"]], jsii.get(self, "parameterInput"))

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
    def parameter(self) -> typing.List["DbParameterGroupParameter"]:
        return typing.cast(typing.List["DbParameterGroupParameter"], jsii.get(self, "parameter"))

    @parameter.setter
    def parameter(self, value: typing.List["DbParameterGroupParameter"]) -> None:
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
    jsii_type="@cdktf/provider-aws.rds.DbParameterGroupConfig",
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
class DbParameterGroupConfig(cdktf.TerraformMetaArguments):
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
        parameter: typing.Optional[typing.Sequence["DbParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#family DbParameterGroup#family}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#description DbParameterGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#name DbParameterGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#name_prefix DbParameterGroup#name_prefix}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#parameter DbParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#tags DbParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#tags_all DbParameterGroup#tags_all}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#family DbParameterGroup#family}.'''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#description DbParameterGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#name DbParameterGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#name_prefix DbParameterGroup#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(self) -> typing.Optional[typing.List["DbParameterGroupParameter"]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#parameter DbParameterGroup#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.List["DbParameterGroupParameter"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#tags DbParameterGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#tags_all DbParameterGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbParameterGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbParameterGroupParameter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value", "apply_method": "applyMethod"},
)
class DbParameterGroupParameter:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: builtins.str,
        apply_method: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#name DbParameterGroup#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#value DbParameterGroup#value}.
        :param apply_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#apply_method DbParameterGroup#apply_method}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }
        if apply_method is not None:
            self._values["apply_method"] = apply_method

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#name DbParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#value DbParameterGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def apply_method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_parameter_group#apply_method DbParameterGroup#apply_method}.'''
        result = self._values.get("apply_method")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbParameterGroupParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbProxy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbProxy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_proxy aws_db_proxy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        auth: typing.Sequence["DbProxyAuth"],
        engine_family: builtins.str,
        name: builtins.str,
        role_arn: builtins.str,
        vpc_subnet_ids: typing.Sequence[builtins.str],
        debug_logging: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        idle_client_timeout: typing.Optional[jsii.Number] = None,
        require_tls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbProxyTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_proxy aws_db_proxy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param auth: auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#auth DbProxy#auth}
        :param engine_family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#engine_family DbProxy#engine_family}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#name DbProxy#name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#role_arn DbProxy#role_arn}.
        :param vpc_subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#vpc_subnet_ids DbProxy#vpc_subnet_ids}.
        :param debug_logging: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#debug_logging DbProxy#debug_logging}.
        :param idle_client_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#idle_client_timeout DbProxy#idle_client_timeout}.
        :param require_tls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#require_tls DbProxy#require_tls}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#tags DbProxy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#tags_all DbProxy#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#timeouts DbProxy#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#vpc_security_group_ids DbProxy#vpc_security_group_ids}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbProxyConfig(
            auth=auth,
            engine_family=engine_family,
            name=name,
            role_arn=role_arn,
            vpc_subnet_ids=vpc_subnet_ids,
            debug_logging=debug_logging,
            idle_client_timeout=idle_client_timeout,
            require_tls=require_tls,
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
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#create DbProxy#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#delete DbProxy#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#update DbProxy#update}.
        '''
        value = DbProxyTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDebugLogging")
    def reset_debug_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDebugLogging", []))

    @jsii.member(jsii_name="resetIdleClientTimeout")
    def reset_idle_client_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdleClientTimeout", []))

    @jsii.member(jsii_name="resetRequireTls")
    def reset_require_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireTls", []))

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
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DbProxyTimeoutsOutputReference":
        return typing.cast("DbProxyTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authInput")
    def auth_input(self) -> typing.Optional[typing.List["DbProxyAuth"]]:
        return typing.cast(typing.Optional[typing.List["DbProxyAuth"]], jsii.get(self, "authInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="debugLoggingInput")
    def debug_logging_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "debugLoggingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineFamilyInput")
    def engine_family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineFamilyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleClientTimeoutInput")
    def idle_client_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idleClientTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireTlsInput")
    def require_tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "requireTlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

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
    def timeouts_input(self) -> typing.Optional["DbProxyTimeouts"]:
        return typing.cast(typing.Optional["DbProxyTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIdsInput")
    def vpc_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnetIdsInput")
    def vpc_subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSubnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auth")
    def auth(self) -> typing.List["DbProxyAuth"]:
        return typing.cast(typing.List["DbProxyAuth"], jsii.get(self, "auth"))

    @auth.setter
    def auth(self, value: typing.List["DbProxyAuth"]) -> None:
        jsii.set(self, "auth", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="debugLogging")
    def debug_logging(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "debugLogging"))

    @debug_logging.setter
    def debug_logging(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "debugLogging", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineFamily")
    def engine_family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineFamily"))

    @engine_family.setter
    def engine_family(self, value: builtins.str) -> None:
        jsii.set(self, "engineFamily", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idleClientTimeout")
    def idle_client_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleClientTimeout"))

    @idle_client_timeout.setter
    def idle_client_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "idleClientTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requireTls")
    def require_tls(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "requireTls"))

    @require_tls.setter
    def require_tls(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "requireTls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnetIds")
    def vpc_subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSubnetIds"))

    @vpc_subnet_ids.setter
    def vpc_subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "vpcSubnetIds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbProxyAuth",
    jsii_struct_bases=[],
    name_mapping={
        "auth_scheme": "authScheme",
        "description": "description",
        "iam_auth": "iamAuth",
        "secret_arn": "secretArn",
    },
)
class DbProxyAuth:
    def __init__(
        self,
        *,
        auth_scheme: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        iam_auth: typing.Optional[builtins.str] = None,
        secret_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_scheme: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#auth_scheme DbProxy#auth_scheme}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#description DbProxy#description}.
        :param iam_auth: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#iam_auth DbProxy#iam_auth}.
        :param secret_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#secret_arn DbProxy#secret_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if auth_scheme is not None:
            self._values["auth_scheme"] = auth_scheme
        if description is not None:
            self._values["description"] = description
        if iam_auth is not None:
            self._values["iam_auth"] = iam_auth
        if secret_arn is not None:
            self._values["secret_arn"] = secret_arn

    @builtins.property
    def auth_scheme(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#auth_scheme DbProxy#auth_scheme}.'''
        result = self._values.get("auth_scheme")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#description DbProxy#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_auth(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#iam_auth DbProxy#iam_auth}.'''
        result = self._values.get("iam_auth")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#secret_arn DbProxy#secret_arn}.'''
        result = self._values.get("secret_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbProxyAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbProxyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "auth": "auth",
        "engine_family": "engineFamily",
        "name": "name",
        "role_arn": "roleArn",
        "vpc_subnet_ids": "vpcSubnetIds",
        "debug_logging": "debugLogging",
        "idle_client_timeout": "idleClientTimeout",
        "require_tls": "requireTls",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class DbProxyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        auth: typing.Sequence[DbProxyAuth],
        engine_family: builtins.str,
        name: builtins.str,
        role_arn: builtins.str,
        vpc_subnet_ids: typing.Sequence[builtins.str],
        debug_logging: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        idle_client_timeout: typing.Optional[jsii.Number] = None,
        require_tls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbProxyTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param auth: auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#auth DbProxy#auth}
        :param engine_family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#engine_family DbProxy#engine_family}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#name DbProxy#name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#role_arn DbProxy#role_arn}.
        :param vpc_subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#vpc_subnet_ids DbProxy#vpc_subnet_ids}.
        :param debug_logging: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#debug_logging DbProxy#debug_logging}.
        :param idle_client_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#idle_client_timeout DbProxy#idle_client_timeout}.
        :param require_tls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#require_tls DbProxy#require_tls}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#tags DbProxy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#tags_all DbProxy#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#timeouts DbProxy#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#vpc_security_group_ids DbProxy#vpc_security_group_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DbProxyTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "auth": auth,
            "engine_family": engine_family,
            "name": name,
            "role_arn": role_arn,
            "vpc_subnet_ids": vpc_subnet_ids,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if debug_logging is not None:
            self._values["debug_logging"] = debug_logging
        if idle_client_timeout is not None:
            self._values["idle_client_timeout"] = idle_client_timeout
        if require_tls is not None:
            self._values["require_tls"] = require_tls
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
    def auth(self) -> typing.List[DbProxyAuth]:
        '''auth block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#auth DbProxy#auth}
        '''
        result = self._values.get("auth")
        assert result is not None, "Required property 'auth' is missing"
        return typing.cast(typing.List[DbProxyAuth], result)

    @builtins.property
    def engine_family(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#engine_family DbProxy#engine_family}.'''
        result = self._values.get("engine_family")
        assert result is not None, "Required property 'engine_family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#name DbProxy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#role_arn DbProxy#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#vpc_subnet_ids DbProxy#vpc_subnet_ids}.'''
        result = self._values.get("vpc_subnet_ids")
        assert result is not None, "Required property 'vpc_subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def debug_logging(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#debug_logging DbProxy#debug_logging}.'''
        result = self._values.get("debug_logging")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def idle_client_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#idle_client_timeout DbProxy#idle_client_timeout}.'''
        result = self._values.get("idle_client_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def require_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#require_tls DbProxy#require_tls}.'''
        result = self._values.get("require_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#tags DbProxy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#tags_all DbProxy#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DbProxyTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#timeouts DbProxy#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DbProxyTimeouts"], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#vpc_security_group_ids DbProxy#vpc_security_group_ids}.'''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbProxyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbProxyDefaultTargetGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbProxyDefaultTargetGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group aws_db_proxy_default_target_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_proxy_name: builtins.str,
        connection_pool_config: typing.Optional["DbProxyDefaultTargetGroupConnectionPoolConfig"] = None,
        timeouts: typing.Optional["DbProxyDefaultTargetGroupTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group aws_db_proxy_default_target_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_proxy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#db_proxy_name DbProxyDefaultTargetGroup#db_proxy_name}.
        :param connection_pool_config: connection_pool_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#connection_pool_config DbProxyDefaultTargetGroup#connection_pool_config}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#timeouts DbProxyDefaultTargetGroup#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbProxyDefaultTargetGroupConfig(
            db_proxy_name=db_proxy_name,
            connection_pool_config=connection_pool_config,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putConnectionPoolConfig")
    def put_connection_pool_config(
        self,
        *,
        connection_borrow_timeout: typing.Optional[jsii.Number] = None,
        init_query: typing.Optional[builtins.str] = None,
        max_connections_percent: typing.Optional[jsii.Number] = None,
        max_idle_connections_percent: typing.Optional[jsii.Number] = None,
        session_pinning_filters: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection_borrow_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#connection_borrow_timeout DbProxyDefaultTargetGroup#connection_borrow_timeout}.
        :param init_query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#init_query DbProxyDefaultTargetGroup#init_query}.
        :param max_connections_percent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#max_connections_percent DbProxyDefaultTargetGroup#max_connections_percent}.
        :param max_idle_connections_percent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#max_idle_connections_percent DbProxyDefaultTargetGroup#max_idle_connections_percent}.
        :param session_pinning_filters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#session_pinning_filters DbProxyDefaultTargetGroup#session_pinning_filters}.
        '''
        value = DbProxyDefaultTargetGroupConnectionPoolConfig(
            connection_borrow_timeout=connection_borrow_timeout,
            init_query=init_query,
            max_connections_percent=max_connections_percent,
            max_idle_connections_percent=max_idle_connections_percent,
            session_pinning_filters=session_pinning_filters,
        )

        return typing.cast(None, jsii.invoke(self, "putConnectionPoolConfig", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#create DbProxyDefaultTargetGroup#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#update DbProxyDefaultTargetGroup#update}.
        '''
        value = DbProxyDefaultTargetGroupTimeouts(create=create, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetConnectionPoolConfig")
    def reset_connection_pool_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionPoolConfig", []))

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
    @jsii.member(jsii_name="connectionPoolConfig")
    def connection_pool_config(
        self,
    ) -> "DbProxyDefaultTargetGroupConnectionPoolConfigOutputReference":
        return typing.cast("DbProxyDefaultTargetGroupConnectionPoolConfigOutputReference", jsii.get(self, "connectionPoolConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DbProxyDefaultTargetGroupTimeoutsOutputReference":
        return typing.cast("DbProxyDefaultTargetGroupTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionPoolConfigInput")
    def connection_pool_config_input(
        self,
    ) -> typing.Optional["DbProxyDefaultTargetGroupConnectionPoolConfig"]:
        return typing.cast(typing.Optional["DbProxyDefaultTargetGroupConnectionPoolConfig"], jsii.get(self, "connectionPoolConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbProxyNameInput")
    def db_proxy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbProxyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["DbProxyDefaultTargetGroupTimeouts"]:
        return typing.cast(typing.Optional["DbProxyDefaultTargetGroupTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbProxyName")
    def db_proxy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbProxyName"))

    @db_proxy_name.setter
    def db_proxy_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbProxyName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbProxyDefaultTargetGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_proxy_name": "dbProxyName",
        "connection_pool_config": "connectionPoolConfig",
        "timeouts": "timeouts",
    },
)
class DbProxyDefaultTargetGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_proxy_name: builtins.str,
        connection_pool_config: typing.Optional["DbProxyDefaultTargetGroupConnectionPoolConfig"] = None,
        timeouts: typing.Optional["DbProxyDefaultTargetGroupTimeouts"] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_proxy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#db_proxy_name DbProxyDefaultTargetGroup#db_proxy_name}.
        :param connection_pool_config: connection_pool_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#connection_pool_config DbProxyDefaultTargetGroup#connection_pool_config}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#timeouts DbProxyDefaultTargetGroup#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(connection_pool_config, dict):
            connection_pool_config = DbProxyDefaultTargetGroupConnectionPoolConfig(**connection_pool_config)
        if isinstance(timeouts, dict):
            timeouts = DbProxyDefaultTargetGroupTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "db_proxy_name": db_proxy_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if connection_pool_config is not None:
            self._values["connection_pool_config"] = connection_pool_config
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
    def db_proxy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#db_proxy_name DbProxyDefaultTargetGroup#db_proxy_name}.'''
        result = self._values.get("db_proxy_name")
        assert result is not None, "Required property 'db_proxy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connection_pool_config(
        self,
    ) -> typing.Optional["DbProxyDefaultTargetGroupConnectionPoolConfig"]:
        '''connection_pool_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#connection_pool_config DbProxyDefaultTargetGroup#connection_pool_config}
        '''
        result = self._values.get("connection_pool_config")
        return typing.cast(typing.Optional["DbProxyDefaultTargetGroupConnectionPoolConfig"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DbProxyDefaultTargetGroupTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#timeouts DbProxyDefaultTargetGroup#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DbProxyDefaultTargetGroupTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbProxyDefaultTargetGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbProxyDefaultTargetGroupConnectionPoolConfig",
    jsii_struct_bases=[],
    name_mapping={
        "connection_borrow_timeout": "connectionBorrowTimeout",
        "init_query": "initQuery",
        "max_connections_percent": "maxConnectionsPercent",
        "max_idle_connections_percent": "maxIdleConnectionsPercent",
        "session_pinning_filters": "sessionPinningFilters",
    },
)
class DbProxyDefaultTargetGroupConnectionPoolConfig:
    def __init__(
        self,
        *,
        connection_borrow_timeout: typing.Optional[jsii.Number] = None,
        init_query: typing.Optional[builtins.str] = None,
        max_connections_percent: typing.Optional[jsii.Number] = None,
        max_idle_connections_percent: typing.Optional[jsii.Number] = None,
        session_pinning_filters: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection_borrow_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#connection_borrow_timeout DbProxyDefaultTargetGroup#connection_borrow_timeout}.
        :param init_query: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#init_query DbProxyDefaultTargetGroup#init_query}.
        :param max_connections_percent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#max_connections_percent DbProxyDefaultTargetGroup#max_connections_percent}.
        :param max_idle_connections_percent: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#max_idle_connections_percent DbProxyDefaultTargetGroup#max_idle_connections_percent}.
        :param session_pinning_filters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#session_pinning_filters DbProxyDefaultTargetGroup#session_pinning_filters}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if connection_borrow_timeout is not None:
            self._values["connection_borrow_timeout"] = connection_borrow_timeout
        if init_query is not None:
            self._values["init_query"] = init_query
        if max_connections_percent is not None:
            self._values["max_connections_percent"] = max_connections_percent
        if max_idle_connections_percent is not None:
            self._values["max_idle_connections_percent"] = max_idle_connections_percent
        if session_pinning_filters is not None:
            self._values["session_pinning_filters"] = session_pinning_filters

    @builtins.property
    def connection_borrow_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#connection_borrow_timeout DbProxyDefaultTargetGroup#connection_borrow_timeout}.'''
        result = self._values.get("connection_borrow_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def init_query(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#init_query DbProxyDefaultTargetGroup#init_query}.'''
        result = self._values.get("init_query")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_connections_percent(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#max_connections_percent DbProxyDefaultTargetGroup#max_connections_percent}.'''
        result = self._values.get("max_connections_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections_percent(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#max_idle_connections_percent DbProxyDefaultTargetGroup#max_idle_connections_percent}.'''
        result = self._values.get("max_idle_connections_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def session_pinning_filters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#session_pinning_filters DbProxyDefaultTargetGroup#session_pinning_filters}.'''
        result = self._values.get("session_pinning_filters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbProxyDefaultTargetGroupConnectionPoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbProxyDefaultTargetGroupConnectionPoolConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbProxyDefaultTargetGroupConnectionPoolConfigOutputReference",
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

    @jsii.member(jsii_name="resetConnectionBorrowTimeout")
    def reset_connection_borrow_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionBorrowTimeout", []))

    @jsii.member(jsii_name="resetInitQuery")
    def reset_init_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInitQuery", []))

    @jsii.member(jsii_name="resetMaxConnectionsPercent")
    def reset_max_connections_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionsPercent", []))

    @jsii.member(jsii_name="resetMaxIdleConnectionsPercent")
    def reset_max_idle_connections_percent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnectionsPercent", []))

    @jsii.member(jsii_name="resetSessionPinningFilters")
    def reset_session_pinning_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionPinningFilters", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionBorrowTimeoutInput")
    def connection_borrow_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectionBorrowTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="initQueryInput")
    def init_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "initQueryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxConnectionsPercentInput")
    def max_connections_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionsPercentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxIdleConnectionsPercentInput")
    def max_idle_connections_percent_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsPercentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionPinningFiltersInput")
    def session_pinning_filters_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sessionPinningFiltersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionBorrowTimeout")
    def connection_borrow_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectionBorrowTimeout"))

    @connection_borrow_timeout.setter
    def connection_borrow_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "connectionBorrowTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="initQuery")
    def init_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "initQuery"))

    @init_query.setter
    def init_query(self, value: builtins.str) -> None:
        jsii.set(self, "initQuery", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxConnectionsPercent")
    def max_connections_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionsPercent"))

    @max_connections_percent.setter
    def max_connections_percent(self, value: jsii.Number) -> None:
        jsii.set(self, "maxConnectionsPercent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxIdleConnectionsPercent")
    def max_idle_connections_percent(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnectionsPercent"))

    @max_idle_connections_percent.setter
    def max_idle_connections_percent(self, value: jsii.Number) -> None:
        jsii.set(self, "maxIdleConnectionsPercent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionPinningFilters")
    def session_pinning_filters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sessionPinningFilters"))

    @session_pinning_filters.setter
    def session_pinning_filters(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "sessionPinningFilters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DbProxyDefaultTargetGroupConnectionPoolConfig]:
        return typing.cast(typing.Optional[DbProxyDefaultTargetGroupConnectionPoolConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DbProxyDefaultTargetGroupConnectionPoolConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbProxyDefaultTargetGroupTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "update": "update"},
)
class DbProxyDefaultTargetGroupTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#create DbProxyDefaultTargetGroup#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#update DbProxyDefaultTargetGroup#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#create DbProxyDefaultTargetGroup#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_default_target_group#update DbProxyDefaultTargetGroup#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbProxyDefaultTargetGroupTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbProxyDefaultTargetGroupTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbProxyDefaultTargetGroupTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

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
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DbProxyDefaultTargetGroupTimeouts]:
        return typing.cast(typing.Optional[DbProxyDefaultTargetGroupTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DbProxyDefaultTargetGroupTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DbProxyEndpoint(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbProxyEndpoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint aws_db_proxy_endpoint}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_proxy_endpoint_name: builtins.str,
        db_proxy_name: builtins.str,
        vpc_subnet_ids: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        target_role: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["DbProxyEndpointTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint aws_db_proxy_endpoint} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_proxy_endpoint_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#db_proxy_endpoint_name DbProxyEndpoint#db_proxy_endpoint_name}.
        :param db_proxy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#db_proxy_name DbProxyEndpoint#db_proxy_name}.
        :param vpc_subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#vpc_subnet_ids DbProxyEndpoint#vpc_subnet_ids}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#tags DbProxyEndpoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#tags_all DbProxyEndpoint#tags_all}.
        :param target_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#target_role DbProxyEndpoint#target_role}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#timeouts DbProxyEndpoint#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#vpc_security_group_ids DbProxyEndpoint#vpc_security_group_ids}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbProxyEndpointConfig(
            db_proxy_endpoint_name=db_proxy_endpoint_name,
            db_proxy_name=db_proxy_name,
            vpc_subnet_ids=vpc_subnet_ids,
            tags=tags,
            tags_all=tags_all,
            target_role=target_role,
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
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#create DbProxyEndpoint#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#delete DbProxyEndpoint#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#update DbProxyEndpoint#update}.
        '''
        value = DbProxyEndpointTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTargetRole")
    def reset_target_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetRole", []))

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
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isDefault")
    def is_default(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "isDefault"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DbProxyEndpointTimeoutsOutputReference":
        return typing.cast("DbProxyEndpointTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbProxyEndpointNameInput")
    def db_proxy_endpoint_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbProxyEndpointNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbProxyNameInput")
    def db_proxy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbProxyNameInput"))

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
    @jsii.member(jsii_name="targetRoleInput")
    def target_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["DbProxyEndpointTimeouts"]:
        return typing.cast(typing.Optional["DbProxyEndpointTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIdsInput")
    def vpc_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnetIdsInput")
    def vpc_subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSubnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbProxyEndpointName")
    def db_proxy_endpoint_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbProxyEndpointName"))

    @db_proxy_endpoint_name.setter
    def db_proxy_endpoint_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbProxyEndpointName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbProxyName")
    def db_proxy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbProxyName"))

    @db_proxy_name.setter
    def db_proxy_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbProxyName", value)

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
    @jsii.member(jsii_name="targetRole")
    def target_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetRole"))

    @target_role.setter
    def target_role(self, value: builtins.str) -> None:
        jsii.set(self, "targetRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSecurityGroupIds"))

    @vpc_security_group_ids.setter
    def vpc_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "vpcSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnetIds")
    def vpc_subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcSubnetIds"))

    @vpc_subnet_ids.setter
    def vpc_subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "vpcSubnetIds", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbProxyEndpointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_proxy_endpoint_name": "dbProxyEndpointName",
        "db_proxy_name": "dbProxyName",
        "vpc_subnet_ids": "vpcSubnetIds",
        "tags": "tags",
        "tags_all": "tagsAll",
        "target_role": "targetRole",
        "timeouts": "timeouts",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class DbProxyEndpointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_proxy_endpoint_name: builtins.str,
        db_proxy_name: builtins.str,
        vpc_subnet_ids: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        target_role: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["DbProxyEndpointTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_proxy_endpoint_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#db_proxy_endpoint_name DbProxyEndpoint#db_proxy_endpoint_name}.
        :param db_proxy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#db_proxy_name DbProxyEndpoint#db_proxy_name}.
        :param vpc_subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#vpc_subnet_ids DbProxyEndpoint#vpc_subnet_ids}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#tags DbProxyEndpoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#tags_all DbProxyEndpoint#tags_all}.
        :param target_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#target_role DbProxyEndpoint#target_role}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#timeouts DbProxyEndpoint#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#vpc_security_group_ids DbProxyEndpoint#vpc_security_group_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DbProxyEndpointTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "db_proxy_endpoint_name": db_proxy_endpoint_name,
            "db_proxy_name": db_proxy_name,
            "vpc_subnet_ids": vpc_subnet_ids,
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
        if target_role is not None:
            self._values["target_role"] = target_role
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
    def db_proxy_endpoint_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#db_proxy_endpoint_name DbProxyEndpoint#db_proxy_endpoint_name}.'''
        result = self._values.get("db_proxy_endpoint_name")
        assert result is not None, "Required property 'db_proxy_endpoint_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_proxy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#db_proxy_name DbProxyEndpoint#db_proxy_name}.'''
        result = self._values.get("db_proxy_name")
        assert result is not None, "Required property 'db_proxy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#vpc_subnet_ids DbProxyEndpoint#vpc_subnet_ids}.'''
        result = self._values.get("vpc_subnet_ids")
        assert result is not None, "Required property 'vpc_subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#tags DbProxyEndpoint#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#tags_all DbProxyEndpoint#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def target_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#target_role DbProxyEndpoint#target_role}.'''
        result = self._values.get("target_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DbProxyEndpointTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#timeouts DbProxyEndpoint#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DbProxyEndpointTimeouts"], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#vpc_security_group_ids DbProxyEndpoint#vpc_security_group_ids}.'''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbProxyEndpointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbProxyEndpointTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class DbProxyEndpointTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#create DbProxyEndpoint#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#delete DbProxyEndpoint#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#update DbProxyEndpoint#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#create DbProxyEndpoint#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#delete DbProxyEndpoint#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_endpoint#update DbProxyEndpoint#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbProxyEndpointTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbProxyEndpointTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbProxyEndpointTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[DbProxyEndpointTimeouts]:
        return typing.cast(typing.Optional[DbProxyEndpointTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DbProxyEndpointTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class DbProxyTarget(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbProxyTarget",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target aws_db_proxy_target}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_proxy_name: builtins.str,
        target_group_name: builtins.str,
        db_cluster_identifier: typing.Optional[builtins.str] = None,
        db_instance_identifier: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target aws_db_proxy_target} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_proxy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#db_proxy_name DbProxyTarget#db_proxy_name}.
        :param target_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#target_group_name DbProxyTarget#target_group_name}.
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#db_cluster_identifier DbProxyTarget#db_cluster_identifier}.
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#db_instance_identifier DbProxyTarget#db_instance_identifier}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbProxyTargetConfig(
            db_proxy_name=db_proxy_name,
            target_group_name=target_group_name,
            db_cluster_identifier=db_cluster_identifier,
            db_instance_identifier=db_instance_identifier,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDbClusterIdentifier")
    def reset_db_cluster_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbClusterIdentifier", []))

    @jsii.member(jsii_name="resetDbInstanceIdentifier")
    def reset_db_instance_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbInstanceIdentifier", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsResourceId")
    def rds_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdsResourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArn")
    def target_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trackedClusterId")
    def tracked_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackedClusterId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterIdentifierInput")
    def db_cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbClusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifierInput")
    def db_instance_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbInstanceIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbProxyNameInput")
    def db_proxy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbProxyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetGroupNameInput")
    def target_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbClusterIdentifier"))

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbClusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceIdentifier"))

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbInstanceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbProxyName")
    def db_proxy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbProxyName"))

    @db_proxy_name.setter
    def db_proxy_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbProxyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetGroupName")
    def target_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetGroupName"))

    @target_group_name.setter
    def target_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "targetGroupName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbProxyTargetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_proxy_name": "dbProxyName",
        "target_group_name": "targetGroupName",
        "db_cluster_identifier": "dbClusterIdentifier",
        "db_instance_identifier": "dbInstanceIdentifier",
    },
)
class DbProxyTargetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_proxy_name: builtins.str,
        target_group_name: builtins.str,
        db_cluster_identifier: typing.Optional[builtins.str] = None,
        db_instance_identifier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_proxy_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#db_proxy_name DbProxyTarget#db_proxy_name}.
        :param target_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#target_group_name DbProxyTarget#target_group_name}.
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#db_cluster_identifier DbProxyTarget#db_cluster_identifier}.
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#db_instance_identifier DbProxyTarget#db_instance_identifier}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "db_proxy_name": db_proxy_name,
            "target_group_name": target_group_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if db_cluster_identifier is not None:
            self._values["db_cluster_identifier"] = db_cluster_identifier
        if db_instance_identifier is not None:
            self._values["db_instance_identifier"] = db_instance_identifier

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
    def db_proxy_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#db_proxy_name DbProxyTarget#db_proxy_name}.'''
        result = self._values.get("db_proxy_name")
        assert result is not None, "Required property 'db_proxy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#target_group_name DbProxyTarget#target_group_name}.'''
        result = self._values.get("target_group_name")
        assert result is not None, "Required property 'target_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#db_cluster_identifier DbProxyTarget#db_cluster_identifier}.'''
        result = self._values.get("db_cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_instance_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy_target#db_instance_identifier DbProxyTarget#db_instance_identifier}.'''
        result = self._values.get("db_instance_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbProxyTargetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbProxyTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class DbProxyTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#create DbProxy#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#delete DbProxy#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#update DbProxy#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#create DbProxy#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#delete DbProxy#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_proxy#update DbProxy#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbProxyTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbProxyTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbProxyTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[DbProxyTimeouts]:
        return typing.cast(typing.Optional[DbProxyTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DbProxyTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class DbSecurityGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbSecurityGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_security_group aws_db_security_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ingress: typing.Sequence["DbSecurityGroupIngress"],
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_security_group aws_db_security_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ingress: ingress block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#ingress DbSecurityGroup#ingress}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#name DbSecurityGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#description DbSecurityGroup#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#tags DbSecurityGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#tags_all DbSecurityGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbSecurityGroupConfig(
            ingress=ingress,
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
    @jsii.member(jsii_name="ingressInput")
    def ingress_input(self) -> typing.Optional[typing.List["DbSecurityGroupIngress"]]:
        return typing.cast(typing.Optional[typing.List["DbSecurityGroupIngress"]], jsii.get(self, "ingressInput"))

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
    @jsii.member(jsii_name="ingress")
    def ingress(self) -> typing.List["DbSecurityGroupIngress"]:
        return typing.cast(typing.List["DbSecurityGroupIngress"], jsii.get(self, "ingress"))

    @ingress.setter
    def ingress(self, value: typing.List["DbSecurityGroupIngress"]) -> None:
        jsii.set(self, "ingress", value)

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
    jsii_type="@cdktf/provider-aws.rds.DbSecurityGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "ingress": "ingress",
        "name": "name",
        "description": "description",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DbSecurityGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        ingress: typing.Sequence["DbSecurityGroupIngress"],
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param ingress: ingress block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#ingress DbSecurityGroup#ingress}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#name DbSecurityGroup#name}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#description DbSecurityGroup#description}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#tags DbSecurityGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#tags_all DbSecurityGroup#tags_all}.
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
    def ingress(self) -> typing.List["DbSecurityGroupIngress"]:
        '''ingress block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#ingress DbSecurityGroup#ingress}
        '''
        result = self._values.get("ingress")
        assert result is not None, "Required property 'ingress' is missing"
        return typing.cast(typing.List["DbSecurityGroupIngress"], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#name DbSecurityGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#description DbSecurityGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#tags DbSecurityGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#tags_all DbSecurityGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbSecurityGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbSecurityGroupIngress",
    jsii_struct_bases=[],
    name_mapping={
        "cidr": "cidr",
        "security_group_id": "securityGroupId",
        "security_group_name": "securityGroupName",
        "security_group_owner_id": "securityGroupOwnerId",
    },
)
class DbSecurityGroupIngress:
    def __init__(
        self,
        *,
        cidr: typing.Optional[builtins.str] = None,
        security_group_id: typing.Optional[builtins.str] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        security_group_owner_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#cidr DbSecurityGroup#cidr}.
        :param security_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#security_group_id DbSecurityGroup#security_group_id}.
        :param security_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#security_group_name DbSecurityGroup#security_group_name}.
        :param security_group_owner_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#security_group_owner_id DbSecurityGroup#security_group_owner_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cidr is not None:
            self._values["cidr"] = cidr
        if security_group_id is not None:
            self._values["security_group_id"] = security_group_id
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name
        if security_group_owner_id is not None:
            self._values["security_group_owner_id"] = security_group_owner_id

    @builtins.property
    def cidr(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#cidr DbSecurityGroup#cidr}.'''
        result = self._values.get("cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#security_group_id DbSecurityGroup#security_group_id}.'''
        result = self._values.get("security_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#security_group_name DbSecurityGroup#security_group_name}.'''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_owner_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_security_group#security_group_owner_id DbSecurityGroup#security_group_owner_id}.'''
        result = self._values.get("security_group_owner_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbSecurityGroupIngress(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbSnapshot(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbSnapshot",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot aws_db_snapshot}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_instance_identifier: builtins.str,
        db_snapshot_identifier: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbSnapshotTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot aws_db_snapshot} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#db_instance_identifier DbSnapshot#db_instance_identifier}.
        :param db_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#db_snapshot_identifier DbSnapshot#db_snapshot_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#tags DbSnapshot#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#tags_all DbSnapshot#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#timeouts DbSnapshot#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbSnapshotConfig(
            db_instance_identifier=db_instance_identifier,
            db_snapshot_identifier=db_snapshot_identifier,
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
    def put_timeouts(self, *, read: typing.Optional[builtins.str] = None) -> None:
        '''
        :param read: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#read DbSnapshot#read}.
        '''
        value = DbSnapshotTimeouts(read=read)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

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
    @jsii.member(jsii_name="allocatedStorage")
    def allocated_storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "allocatedStorage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSnapshotArn")
    def db_snapshot_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbSnapshotArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encrypted")
    def encrypted(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "encrypted"))

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
    @jsii.member(jsii_name="iops")
    def iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iops"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="licenseModel")
    def license_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "licenseModel"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionGroupName")
    def option_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "optionGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotType")
    def snapshot_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDbSnapshotIdentifier")
    def source_db_snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDbSnapshotIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceRegion")
    def source_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceRegion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "DbSnapshotTimeoutsOutputReference":
        return typing.cast("DbSnapshotTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifierInput")
    def db_instance_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbInstanceIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSnapshotIdentifierInput")
    def db_snapshot_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbSnapshotIdentifierInput"))

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
    def timeouts_input(self) -> typing.Optional["DbSnapshotTimeouts"]:
        return typing.cast(typing.Optional["DbSnapshotTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceIdentifier"))

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbInstanceIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSnapshotIdentifier")
    def db_snapshot_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbSnapshotIdentifier"))

    @db_snapshot_identifier.setter
    def db_snapshot_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbSnapshotIdentifier", value)

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
    jsii_type="@cdktf/provider-aws.rds.DbSnapshotConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_instance_identifier": "dbInstanceIdentifier",
        "db_snapshot_identifier": "dbSnapshotIdentifier",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class DbSnapshotConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_instance_identifier: builtins.str,
        db_snapshot_identifier: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["DbSnapshotTimeouts"] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_instance_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#db_instance_identifier DbSnapshot#db_instance_identifier}.
        :param db_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#db_snapshot_identifier DbSnapshot#db_snapshot_identifier}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#tags DbSnapshot#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#tags_all DbSnapshot#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#timeouts DbSnapshot#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = DbSnapshotTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "db_instance_identifier": db_instance_identifier,
            "db_snapshot_identifier": db_snapshot_identifier,
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
    def db_instance_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#db_instance_identifier DbSnapshot#db_instance_identifier}.'''
        result = self._values.get("db_instance_identifier")
        assert result is not None, "Required property 'db_instance_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_snapshot_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#db_snapshot_identifier DbSnapshot#db_snapshot_identifier}.'''
        result = self._values.get("db_snapshot_identifier")
        assert result is not None, "Required property 'db_snapshot_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#tags DbSnapshot#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#tags_all DbSnapshot#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["DbSnapshotTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#timeouts DbSnapshot#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["DbSnapshotTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbSnapshotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.DbSnapshotTimeouts",
    jsii_struct_bases=[],
    name_mapping={"read": "read"},
)
class DbSnapshotTimeouts:
    def __init__(self, *, read: typing.Optional[builtins.str] = None) -> None:
        '''
        :param read: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#read DbSnapshot#read}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if read is not None:
            self._values["read"] = read

    @builtins.property
    def read(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_snapshot#read DbSnapshot#read}.'''
        result = self._values.get("read")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbSnapshotTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DbSnapshotTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbSnapshotTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetRead")
    def reset_read(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRead", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readInput")
    def read_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="read")
    def read(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "read"))

    @read.setter
    def read(self, value: builtins.str) -> None:
        jsii.set(self, "read", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DbSnapshotTimeouts]:
        return typing.cast(typing.Optional[DbSnapshotTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DbSnapshotTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class DbSubnetGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.DbSubnetGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group aws_db_subnet_group}.'''

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
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group aws_db_subnet_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#subnet_ids DbSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#description DbSubnetGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#name DbSubnetGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#name_prefix DbSubnetGroup#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#tags DbSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#tags_all DbSubnetGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DbSubnetGroupConfig(
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
    jsii_type="@cdktf/provider-aws.rds.DbSubnetGroupConfig",
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
class DbSubnetGroupConfig(cdktf.TerraformMetaArguments):
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
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#subnet_ids DbSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#description DbSubnetGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#name DbSubnetGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#name_prefix DbSubnetGroup#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#tags DbSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#tags_all DbSubnetGroup#tags_all}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#subnet_ids DbSubnetGroup#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#description DbSubnetGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#name DbSubnetGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#name_prefix DbSubnetGroup#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#tags DbSubnetGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/db_subnet_group#tags_all DbSubnetGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DbSubnetGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsCluster(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster aws_rds_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allow_major_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        backtrack_window: typing.Optional[jsii.Number] = None,
        backup_retention_period: typing.Optional[jsii.Number] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_identifier_prefix: typing.Optional[builtins.str] = None,
        cluster_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        copy_tags_to_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        database_name: typing.Optional[builtins.str] = None,
        db_cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        db_instance_parameter_group_name: typing.Optional[builtins.str] = None,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enabled_cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        enable_global_write_forwarding: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_http_endpoint: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_mode: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        global_cluster_identifier: typing.Optional[builtins.str] = None,
        iam_database_authentication_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        master_password: typing.Optional[builtins.str] = None,
        master_username: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        replication_source_identifier: typing.Optional[builtins.str] = None,
        restore_to_point_in_time: typing.Optional["RdsClusterRestoreToPointInTime"] = None,
        s3_import: typing.Optional["RdsClusterS3Import"] = None,
        scaling_configuration: typing.Optional["RdsClusterScalingConfiguration"] = None,
        skip_final_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        source_region: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["RdsClusterTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster aws_rds_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allow_major_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#allow_major_version_upgrade RdsCluster#allow_major_version_upgrade}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#apply_immediately RdsCluster#apply_immediately}.
        :param availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#availability_zones RdsCluster#availability_zones}.
        :param backtrack_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#backtrack_window RdsCluster#backtrack_window}.
        :param backup_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#backup_retention_period RdsCluster#backup_retention_period}.
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#cluster_identifier RdsCluster#cluster_identifier}.
        :param cluster_identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#cluster_identifier_prefix RdsCluster#cluster_identifier_prefix}.
        :param cluster_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#cluster_members RdsCluster#cluster_members}.
        :param copy_tags_to_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#copy_tags_to_snapshot RdsCluster#copy_tags_to_snapshot}.
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#database_name RdsCluster#database_name}.
        :param db_cluster_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#db_cluster_parameter_group_name RdsCluster#db_cluster_parameter_group_name}.
        :param db_instance_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#db_instance_parameter_group_name RdsCluster#db_instance_parameter_group_name}.
        :param db_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#db_subnet_group_name RdsCluster#db_subnet_group_name}.
        :param deletion_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#deletion_protection RdsCluster#deletion_protection}.
        :param enabled_cloudwatch_logs_exports: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#enabled_cloudwatch_logs_exports RdsCluster#enabled_cloudwatch_logs_exports}.
        :param enable_global_write_forwarding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#enable_global_write_forwarding RdsCluster#enable_global_write_forwarding}.
        :param enable_http_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#enable_http_endpoint RdsCluster#enable_http_endpoint}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#engine RdsCluster#engine}.
        :param engine_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#engine_mode RdsCluster#engine_mode}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#engine_version RdsCluster#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#final_snapshot_identifier RdsCluster#final_snapshot_identifier}.
        :param global_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#global_cluster_identifier RdsCluster#global_cluster_identifier}.
        :param iam_database_authentication_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#iam_database_authentication_enabled RdsCluster#iam_database_authentication_enabled}.
        :param iam_roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#iam_roles RdsCluster#iam_roles}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#kms_key_id RdsCluster#kms_key_id}.
        :param master_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#master_password RdsCluster#master_password}.
        :param master_username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#master_username RdsCluster#master_username}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#port RdsCluster#port}.
        :param preferred_backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#preferred_backup_window RdsCluster#preferred_backup_window}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#preferred_maintenance_window RdsCluster#preferred_maintenance_window}.
        :param replication_source_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#replication_source_identifier RdsCluster#replication_source_identifier}.
        :param restore_to_point_in_time: restore_to_point_in_time block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#restore_to_point_in_time RdsCluster#restore_to_point_in_time}
        :param s3_import: s3_import block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#s3_import RdsCluster#s3_import}
        :param scaling_configuration: scaling_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#scaling_configuration RdsCluster#scaling_configuration}
        :param skip_final_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#skip_final_snapshot RdsCluster#skip_final_snapshot}.
        :param snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#snapshot_identifier RdsCluster#snapshot_identifier}.
        :param source_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_region RdsCluster#source_region}.
        :param storage_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#storage_encrypted RdsCluster#storage_encrypted}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#tags RdsCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#tags_all RdsCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#timeouts RdsCluster#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#vpc_security_group_ids RdsCluster#vpc_security_group_ids}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RdsClusterConfig(
            allow_major_version_upgrade=allow_major_version_upgrade,
            apply_immediately=apply_immediately,
            availability_zones=availability_zones,
            backtrack_window=backtrack_window,
            backup_retention_period=backup_retention_period,
            cluster_identifier=cluster_identifier,
            cluster_identifier_prefix=cluster_identifier_prefix,
            cluster_members=cluster_members,
            copy_tags_to_snapshot=copy_tags_to_snapshot,
            database_name=database_name,
            db_cluster_parameter_group_name=db_cluster_parameter_group_name,
            db_instance_parameter_group_name=db_instance_parameter_group_name,
            db_subnet_group_name=db_subnet_group_name,
            deletion_protection=deletion_protection,
            enabled_cloudwatch_logs_exports=enabled_cloudwatch_logs_exports,
            enable_global_write_forwarding=enable_global_write_forwarding,
            enable_http_endpoint=enable_http_endpoint,
            engine=engine,
            engine_mode=engine_mode,
            engine_version=engine_version,
            final_snapshot_identifier=final_snapshot_identifier,
            global_cluster_identifier=global_cluster_identifier,
            iam_database_authentication_enabled=iam_database_authentication_enabled,
            iam_roles=iam_roles,
            kms_key_id=kms_key_id,
            master_password=master_password,
            master_username=master_username,
            port=port,
            preferred_backup_window=preferred_backup_window,
            preferred_maintenance_window=preferred_maintenance_window,
            replication_source_identifier=replication_source_identifier,
            restore_to_point_in_time=restore_to_point_in_time,
            s3_import=s3_import,
            scaling_configuration=scaling_configuration,
            skip_final_snapshot=skip_final_snapshot,
            snapshot_identifier=snapshot_identifier,
            source_region=source_region,
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

    @jsii.member(jsii_name="putRestoreToPointInTime")
    def put_restore_to_point_in_time(
        self,
        *,
        source_cluster_identifier: builtins.str,
        restore_to_time: typing.Optional[builtins.str] = None,
        restore_type: typing.Optional[builtins.str] = None,
        use_latest_restorable_time: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param source_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_cluster_identifier RdsCluster#source_cluster_identifier}.
        :param restore_to_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#restore_to_time RdsCluster#restore_to_time}.
        :param restore_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#restore_type RdsCluster#restore_type}.
        :param use_latest_restorable_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#use_latest_restorable_time RdsCluster#use_latest_restorable_time}.
        '''
        value = RdsClusterRestoreToPointInTime(
            source_cluster_identifier=source_cluster_identifier,
            restore_to_time=restore_to_time,
            restore_type=restore_type,
            use_latest_restorable_time=use_latest_restorable_time,
        )

        return typing.cast(None, jsii.invoke(self, "putRestoreToPointInTime", [value]))

    @jsii.member(jsii_name="putS3Import")
    def put_s3_import(
        self,
        *,
        bucket_name: builtins.str,
        ingestion_role: builtins.str,
        source_engine: builtins.str,
        source_engine_version: builtins.str,
        bucket_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#bucket_name RdsCluster#bucket_name}.
        :param ingestion_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#ingestion_role RdsCluster#ingestion_role}.
        :param source_engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_engine RdsCluster#source_engine}.
        :param source_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_engine_version RdsCluster#source_engine_version}.
        :param bucket_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#bucket_prefix RdsCluster#bucket_prefix}.
        '''
        value = RdsClusterS3Import(
            bucket_name=bucket_name,
            ingestion_role=ingestion_role,
            source_engine=source_engine,
            source_engine_version=source_engine_version,
            bucket_prefix=bucket_prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putS3Import", [value]))

    @jsii.member(jsii_name="putScalingConfiguration")
    def put_scaling_configuration(
        self,
        *,
        auto_pause: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        seconds_until_auto_pause: typing.Optional[jsii.Number] = None,
        timeout_action: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auto_pause: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#auto_pause RdsCluster#auto_pause}.
        :param max_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#max_capacity RdsCluster#max_capacity}.
        :param min_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#min_capacity RdsCluster#min_capacity}.
        :param seconds_until_auto_pause: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#seconds_until_auto_pause RdsCluster#seconds_until_auto_pause}.
        :param timeout_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#timeout_action RdsCluster#timeout_action}.
        '''
        value = RdsClusterScalingConfiguration(
            auto_pause=auto_pause,
            max_capacity=max_capacity,
            min_capacity=min_capacity,
            seconds_until_auto_pause=seconds_until_auto_pause,
            timeout_action=timeout_action,
        )

        return typing.cast(None, jsii.invoke(self, "putScalingConfiguration", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#create RdsCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#delete RdsCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#update RdsCluster#update}.
        '''
        value = RdsClusterTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAllowMajorVersionUpgrade")
    def reset_allow_major_version_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowMajorVersionUpgrade", []))

    @jsii.member(jsii_name="resetApplyImmediately")
    def reset_apply_immediately(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplyImmediately", []))

    @jsii.member(jsii_name="resetAvailabilityZones")
    def reset_availability_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZones", []))

    @jsii.member(jsii_name="resetBacktrackWindow")
    def reset_backtrack_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBacktrackWindow", []))

    @jsii.member(jsii_name="resetBackupRetentionPeriod")
    def reset_backup_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupRetentionPeriod", []))

    @jsii.member(jsii_name="resetClusterIdentifier")
    def reset_cluster_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterIdentifier", []))

    @jsii.member(jsii_name="resetClusterIdentifierPrefix")
    def reset_cluster_identifier_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterIdentifierPrefix", []))

    @jsii.member(jsii_name="resetClusterMembers")
    def reset_cluster_members(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterMembers", []))

    @jsii.member(jsii_name="resetCopyTagsToSnapshot")
    def reset_copy_tags_to_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToSnapshot", []))

    @jsii.member(jsii_name="resetDatabaseName")
    def reset_database_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseName", []))

    @jsii.member(jsii_name="resetDbClusterParameterGroupName")
    def reset_db_cluster_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbClusterParameterGroupName", []))

    @jsii.member(jsii_name="resetDbInstanceParameterGroupName")
    def reset_db_instance_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbInstanceParameterGroupName", []))

    @jsii.member(jsii_name="resetDbSubnetGroupName")
    def reset_db_subnet_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbSubnetGroupName", []))

    @jsii.member(jsii_name="resetDeletionProtection")
    def reset_deletion_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletionProtection", []))

    @jsii.member(jsii_name="resetEnabledCloudwatchLogsExports")
    def reset_enabled_cloudwatch_logs_exports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabledCloudwatchLogsExports", []))

    @jsii.member(jsii_name="resetEnableGlobalWriteForwarding")
    def reset_enable_global_write_forwarding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableGlobalWriteForwarding", []))

    @jsii.member(jsii_name="resetEnableHttpEndpoint")
    def reset_enable_http_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableHttpEndpoint", []))

    @jsii.member(jsii_name="resetEngine")
    def reset_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngine", []))

    @jsii.member(jsii_name="resetEngineMode")
    def reset_engine_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineMode", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetFinalSnapshotIdentifier")
    def reset_final_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFinalSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetGlobalClusterIdentifier")
    def reset_global_cluster_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlobalClusterIdentifier", []))

    @jsii.member(jsii_name="resetIamDatabaseAuthenticationEnabled")
    def reset_iam_database_authentication_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamDatabaseAuthenticationEnabled", []))

    @jsii.member(jsii_name="resetIamRoles")
    def reset_iam_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamRoles", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetMasterPassword")
    def reset_master_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterPassword", []))

    @jsii.member(jsii_name="resetMasterUsername")
    def reset_master_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMasterUsername", []))

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

    @jsii.member(jsii_name="resetRestoreToPointInTime")
    def reset_restore_to_point_in_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreToPointInTime", []))

    @jsii.member(jsii_name="resetS3Import")
    def reset_s3_import(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Import", []))

    @jsii.member(jsii_name="resetScalingConfiguration")
    def reset_scaling_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScalingConfiguration", []))

    @jsii.member(jsii_name="resetSkipFinalSnapshot")
    def reset_skip_final_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipFinalSnapshot", []))

    @jsii.member(jsii_name="resetSnapshotIdentifier")
    def reset_snapshot_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotIdentifier", []))

    @jsii.member(jsii_name="resetSourceRegion")
    def reset_source_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceRegion", []))

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
    @jsii.member(jsii_name="clusterResourceId")
    def cluster_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterResourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionActual")
    def engine_version_actual(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersionActual"))

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
    @jsii.member(jsii_name="restoreToPointInTime")
    def restore_to_point_in_time(
        self,
    ) -> "RdsClusterRestoreToPointInTimeOutputReference":
        return typing.cast("RdsClusterRestoreToPointInTimeOutputReference", jsii.get(self, "restoreToPointInTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Import")
    def s3_import(self) -> "RdsClusterS3ImportOutputReference":
        return typing.cast("RdsClusterS3ImportOutputReference", jsii.get(self, "s3Import"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scalingConfiguration")
    def scaling_configuration(self) -> "RdsClusterScalingConfigurationOutputReference":
        return typing.cast("RdsClusterScalingConfigurationOutputReference", jsii.get(self, "scalingConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "RdsClusterTimeoutsOutputReference":
        return typing.cast("RdsClusterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMajorVersionUpgradeInput")
    def allow_major_version_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowMajorVersionUpgradeInput"))

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
    @jsii.member(jsii_name="backtrackWindowInput")
    def backtrack_window_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backtrackWindowInput"))

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
    @jsii.member(jsii_name="clusterMembersInput")
    def cluster_members_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "clusterMembersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToSnapshotInput")
    def copy_tags_to_snapshot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToSnapshotInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseNameInput")
    def database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterParameterGroupNameInput")
    def db_cluster_parameter_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbClusterParameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceParameterGroupNameInput")
    def db_instance_parameter_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbInstanceParameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupNameInput")
    def db_subnet_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbSubnetGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deletionProtectionInput")
    def deletion_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deletionProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledCloudwatchLogsExportsInput")
    def enabled_cloudwatch_logs_exports_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "enabledCloudwatchLogsExportsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableGlobalWriteForwardingInput")
    def enable_global_write_forwarding_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableGlobalWriteForwardingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableHttpEndpointInput")
    def enable_http_endpoint_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableHttpEndpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineInput")
    def engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineModeInput")
    def engine_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionInput")
    def engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="finalSnapshotIdentifierInput")
    def final_snapshot_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "finalSnapshotIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalClusterIdentifierInput")
    def global_cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "globalClusterIdentifierInput"))

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
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterPasswordInput")
    def master_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "masterPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterUsernameInput")
    def master_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "masterUsernameInput"))

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
    @jsii.member(jsii_name="restoreToPointInTimeInput")
    def restore_to_point_in_time_input(
        self,
    ) -> typing.Optional["RdsClusterRestoreToPointInTime"]:
        return typing.cast(typing.Optional["RdsClusterRestoreToPointInTime"], jsii.get(self, "restoreToPointInTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ImportInput")
    def s3_import_input(self) -> typing.Optional["RdsClusterS3Import"]:
        return typing.cast(typing.Optional["RdsClusterS3Import"], jsii.get(self, "s3ImportInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scalingConfigurationInput")
    def scaling_configuration_input(
        self,
    ) -> typing.Optional["RdsClusterScalingConfiguration"]:
        return typing.cast(typing.Optional["RdsClusterScalingConfiguration"], jsii.get(self, "scalingConfigurationInput"))

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
    @jsii.member(jsii_name="sourceRegionInput")
    def source_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceRegionInput"))

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
    def timeouts_input(self) -> typing.Optional["RdsClusterTimeouts"]:
        return typing.cast(typing.Optional["RdsClusterTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSecurityGroupIdsInput")
    def vpc_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowMajorVersionUpgrade")
    def allow_major_version_upgrade(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowMajorVersionUpgrade"))

    @allow_major_version_upgrade.setter
    def allow_major_version_upgrade(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowMajorVersionUpgrade", value)

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
    @jsii.member(jsii_name="backtrackWindow")
    def backtrack_window(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backtrackWindow"))

    @backtrack_window.setter
    def backtrack_window(self, value: jsii.Number) -> None:
        jsii.set(self, "backtrackWindow", value)

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
    @jsii.member(jsii_name="clusterMembers")
    def cluster_members(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "clusterMembers"))

    @cluster_members.setter
    def cluster_members(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "clusterMembers", value)

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
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterParameterGroupName")
    def db_cluster_parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbClusterParameterGroupName"))

    @db_cluster_parameter_group_name.setter
    def db_cluster_parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbClusterParameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbInstanceParameterGroupName")
    def db_instance_parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbInstanceParameterGroupName"))

    @db_instance_parameter_group_name.setter
    def db_instance_parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbInstanceParameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbSubnetGroupName"))

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbSubnetGroupName", value)

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
    @jsii.member(jsii_name="enabledCloudwatchLogsExports")
    def enabled_cloudwatch_logs_exports(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "enabledCloudwatchLogsExports"))

    @enabled_cloudwatch_logs_exports.setter
    def enabled_cloudwatch_logs_exports(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "enabledCloudwatchLogsExports", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableGlobalWriteForwarding")
    def enable_global_write_forwarding(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableGlobalWriteForwarding"))

    @enable_global_write_forwarding.setter
    def enable_global_write_forwarding(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableGlobalWriteForwarding", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableHttpEndpoint")
    def enable_http_endpoint(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableHttpEndpoint"))

    @enable_http_endpoint.setter
    def enable_http_endpoint(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableHttpEndpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @engine.setter
    def engine(self, value: builtins.str) -> None:
        jsii.set(self, "engine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineMode")
    def engine_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineMode"))

    @engine_mode.setter
    def engine_mode(self, value: builtins.str) -> None:
        jsii.set(self, "engineMode", value)

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
    @jsii.member(jsii_name="globalClusterIdentifier")
    def global_cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalClusterIdentifier"))

    @global_cluster_identifier.setter
    def global_cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "globalClusterIdentifier", value)

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
    @jsii.member(jsii_name="sourceRegion")
    def source_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceRegion"))

    @source_region.setter
    def source_region(self, value: builtins.str) -> None:
        jsii.set(self, "sourceRegion", value)

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
    jsii_type="@cdktf/provider-aws.rds.RdsClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "allow_major_version_upgrade": "allowMajorVersionUpgrade",
        "apply_immediately": "applyImmediately",
        "availability_zones": "availabilityZones",
        "backtrack_window": "backtrackWindow",
        "backup_retention_period": "backupRetentionPeriod",
        "cluster_identifier": "clusterIdentifier",
        "cluster_identifier_prefix": "clusterIdentifierPrefix",
        "cluster_members": "clusterMembers",
        "copy_tags_to_snapshot": "copyTagsToSnapshot",
        "database_name": "databaseName",
        "db_cluster_parameter_group_name": "dbClusterParameterGroupName",
        "db_instance_parameter_group_name": "dbInstanceParameterGroupName",
        "db_subnet_group_name": "dbSubnetGroupName",
        "deletion_protection": "deletionProtection",
        "enabled_cloudwatch_logs_exports": "enabledCloudwatchLogsExports",
        "enable_global_write_forwarding": "enableGlobalWriteForwarding",
        "enable_http_endpoint": "enableHttpEndpoint",
        "engine": "engine",
        "engine_mode": "engineMode",
        "engine_version": "engineVersion",
        "final_snapshot_identifier": "finalSnapshotIdentifier",
        "global_cluster_identifier": "globalClusterIdentifier",
        "iam_database_authentication_enabled": "iamDatabaseAuthenticationEnabled",
        "iam_roles": "iamRoles",
        "kms_key_id": "kmsKeyId",
        "master_password": "masterPassword",
        "master_username": "masterUsername",
        "port": "port",
        "preferred_backup_window": "preferredBackupWindow",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "replication_source_identifier": "replicationSourceIdentifier",
        "restore_to_point_in_time": "restoreToPointInTime",
        "s3_import": "s3Import",
        "scaling_configuration": "scalingConfiguration",
        "skip_final_snapshot": "skipFinalSnapshot",
        "snapshot_identifier": "snapshotIdentifier",
        "source_region": "sourceRegion",
        "storage_encrypted": "storageEncrypted",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "vpc_security_group_ids": "vpcSecurityGroupIds",
    },
)
class RdsClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        allow_major_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        apply_immediately: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        availability_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        backtrack_window: typing.Optional[jsii.Number] = None,
        backup_retention_period: typing.Optional[jsii.Number] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        cluster_identifier_prefix: typing.Optional[builtins.str] = None,
        cluster_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        copy_tags_to_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        database_name: typing.Optional[builtins.str] = None,
        db_cluster_parameter_group_name: typing.Optional[builtins.str] = None,
        db_instance_parameter_group_name: typing.Optional[builtins.str] = None,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enabled_cloudwatch_logs_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        enable_global_write_forwarding: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_http_endpoint: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_mode: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_identifier: typing.Optional[builtins.str] = None,
        global_cluster_identifier: typing.Optional[builtins.str] = None,
        iam_database_authentication_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        master_password: typing.Optional[builtins.str] = None,
        master_username: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        replication_source_identifier: typing.Optional[builtins.str] = None,
        restore_to_point_in_time: typing.Optional["RdsClusterRestoreToPointInTime"] = None,
        s3_import: typing.Optional["RdsClusterS3Import"] = None,
        scaling_configuration: typing.Optional["RdsClusterScalingConfiguration"] = None,
        skip_final_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        snapshot_identifier: typing.Optional[builtins.str] = None,
        source_region: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["RdsClusterTimeouts"] = None,
        vpc_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param allow_major_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#allow_major_version_upgrade RdsCluster#allow_major_version_upgrade}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#apply_immediately RdsCluster#apply_immediately}.
        :param availability_zones: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#availability_zones RdsCluster#availability_zones}.
        :param backtrack_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#backtrack_window RdsCluster#backtrack_window}.
        :param backup_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#backup_retention_period RdsCluster#backup_retention_period}.
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#cluster_identifier RdsCluster#cluster_identifier}.
        :param cluster_identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#cluster_identifier_prefix RdsCluster#cluster_identifier_prefix}.
        :param cluster_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#cluster_members RdsCluster#cluster_members}.
        :param copy_tags_to_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#copy_tags_to_snapshot RdsCluster#copy_tags_to_snapshot}.
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#database_name RdsCluster#database_name}.
        :param db_cluster_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#db_cluster_parameter_group_name RdsCluster#db_cluster_parameter_group_name}.
        :param db_instance_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#db_instance_parameter_group_name RdsCluster#db_instance_parameter_group_name}.
        :param db_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#db_subnet_group_name RdsCluster#db_subnet_group_name}.
        :param deletion_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#deletion_protection RdsCluster#deletion_protection}.
        :param enabled_cloudwatch_logs_exports: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#enabled_cloudwatch_logs_exports RdsCluster#enabled_cloudwatch_logs_exports}.
        :param enable_global_write_forwarding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#enable_global_write_forwarding RdsCluster#enable_global_write_forwarding}.
        :param enable_http_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#enable_http_endpoint RdsCluster#enable_http_endpoint}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#engine RdsCluster#engine}.
        :param engine_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#engine_mode RdsCluster#engine_mode}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#engine_version RdsCluster#engine_version}.
        :param final_snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#final_snapshot_identifier RdsCluster#final_snapshot_identifier}.
        :param global_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#global_cluster_identifier RdsCluster#global_cluster_identifier}.
        :param iam_database_authentication_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#iam_database_authentication_enabled RdsCluster#iam_database_authentication_enabled}.
        :param iam_roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#iam_roles RdsCluster#iam_roles}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#kms_key_id RdsCluster#kms_key_id}.
        :param master_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#master_password RdsCluster#master_password}.
        :param master_username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#master_username RdsCluster#master_username}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#port RdsCluster#port}.
        :param preferred_backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#preferred_backup_window RdsCluster#preferred_backup_window}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#preferred_maintenance_window RdsCluster#preferred_maintenance_window}.
        :param replication_source_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#replication_source_identifier RdsCluster#replication_source_identifier}.
        :param restore_to_point_in_time: restore_to_point_in_time block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#restore_to_point_in_time RdsCluster#restore_to_point_in_time}
        :param s3_import: s3_import block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#s3_import RdsCluster#s3_import}
        :param scaling_configuration: scaling_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#scaling_configuration RdsCluster#scaling_configuration}
        :param skip_final_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#skip_final_snapshot RdsCluster#skip_final_snapshot}.
        :param snapshot_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#snapshot_identifier RdsCluster#snapshot_identifier}.
        :param source_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_region RdsCluster#source_region}.
        :param storage_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#storage_encrypted RdsCluster#storage_encrypted}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#tags RdsCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#tags_all RdsCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#timeouts RdsCluster#timeouts}
        :param vpc_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#vpc_security_group_ids RdsCluster#vpc_security_group_ids}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(restore_to_point_in_time, dict):
            restore_to_point_in_time = RdsClusterRestoreToPointInTime(**restore_to_point_in_time)
        if isinstance(s3_import, dict):
            s3_import = RdsClusterS3Import(**s3_import)
        if isinstance(scaling_configuration, dict):
            scaling_configuration = RdsClusterScalingConfiguration(**scaling_configuration)
        if isinstance(timeouts, dict):
            timeouts = RdsClusterTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allow_major_version_upgrade is not None:
            self._values["allow_major_version_upgrade"] = allow_major_version_upgrade
        if apply_immediately is not None:
            self._values["apply_immediately"] = apply_immediately
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if backtrack_window is not None:
            self._values["backtrack_window"] = backtrack_window
        if backup_retention_period is not None:
            self._values["backup_retention_period"] = backup_retention_period
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if cluster_identifier_prefix is not None:
            self._values["cluster_identifier_prefix"] = cluster_identifier_prefix
        if cluster_members is not None:
            self._values["cluster_members"] = cluster_members
        if copy_tags_to_snapshot is not None:
            self._values["copy_tags_to_snapshot"] = copy_tags_to_snapshot
        if database_name is not None:
            self._values["database_name"] = database_name
        if db_cluster_parameter_group_name is not None:
            self._values["db_cluster_parameter_group_name"] = db_cluster_parameter_group_name
        if db_instance_parameter_group_name is not None:
            self._values["db_instance_parameter_group_name"] = db_instance_parameter_group_name
        if db_subnet_group_name is not None:
            self._values["db_subnet_group_name"] = db_subnet_group_name
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if enabled_cloudwatch_logs_exports is not None:
            self._values["enabled_cloudwatch_logs_exports"] = enabled_cloudwatch_logs_exports
        if enable_global_write_forwarding is not None:
            self._values["enable_global_write_forwarding"] = enable_global_write_forwarding
        if enable_http_endpoint is not None:
            self._values["enable_http_endpoint"] = enable_http_endpoint
        if engine is not None:
            self._values["engine"] = engine
        if engine_mode is not None:
            self._values["engine_mode"] = engine_mode
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if final_snapshot_identifier is not None:
            self._values["final_snapshot_identifier"] = final_snapshot_identifier
        if global_cluster_identifier is not None:
            self._values["global_cluster_identifier"] = global_cluster_identifier
        if iam_database_authentication_enabled is not None:
            self._values["iam_database_authentication_enabled"] = iam_database_authentication_enabled
        if iam_roles is not None:
            self._values["iam_roles"] = iam_roles
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if master_password is not None:
            self._values["master_password"] = master_password
        if master_username is not None:
            self._values["master_username"] = master_username
        if port is not None:
            self._values["port"] = port
        if preferred_backup_window is not None:
            self._values["preferred_backup_window"] = preferred_backup_window
        if preferred_maintenance_window is not None:
            self._values["preferred_maintenance_window"] = preferred_maintenance_window
        if replication_source_identifier is not None:
            self._values["replication_source_identifier"] = replication_source_identifier
        if restore_to_point_in_time is not None:
            self._values["restore_to_point_in_time"] = restore_to_point_in_time
        if s3_import is not None:
            self._values["s3_import"] = s3_import
        if scaling_configuration is not None:
            self._values["scaling_configuration"] = scaling_configuration
        if skip_final_snapshot is not None:
            self._values["skip_final_snapshot"] = skip_final_snapshot
        if snapshot_identifier is not None:
            self._values["snapshot_identifier"] = snapshot_identifier
        if source_region is not None:
            self._values["source_region"] = source_region
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
    def allow_major_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#allow_major_version_upgrade RdsCluster#allow_major_version_upgrade}.'''
        result = self._values.get("allow_major_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def apply_immediately(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#apply_immediately RdsCluster#apply_immediately}.'''
        result = self._values.get("apply_immediately")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#availability_zones RdsCluster#availability_zones}.'''
        result = self._values.get("availability_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def backtrack_window(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#backtrack_window RdsCluster#backtrack_window}.'''
        result = self._values.get("backtrack_window")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#backup_retention_period RdsCluster#backup_retention_period}.'''
        result = self._values.get("backup_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#cluster_identifier RdsCluster#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_identifier_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#cluster_identifier_prefix RdsCluster#cluster_identifier_prefix}.'''
        result = self._values.get("cluster_identifier_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_members(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#cluster_members RdsCluster#cluster_members}.'''
        result = self._values.get("cluster_members")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def copy_tags_to_snapshot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#copy_tags_to_snapshot RdsCluster#copy_tags_to_snapshot}.'''
        result = self._values.get("copy_tags_to_snapshot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#database_name RdsCluster#database_name}.'''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_cluster_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#db_cluster_parameter_group_name RdsCluster#db_cluster_parameter_group_name}.'''
        result = self._values.get("db_cluster_parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_instance_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#db_instance_parameter_group_name RdsCluster#db_instance_parameter_group_name}.'''
        result = self._values.get("db_instance_parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#db_subnet_group_name RdsCluster#db_subnet_group_name}.'''
        result = self._values.get("db_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deletion_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#deletion_protection RdsCluster#deletion_protection}.'''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enabled_cloudwatch_logs_exports(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#enabled_cloudwatch_logs_exports RdsCluster#enabled_cloudwatch_logs_exports}.'''
        result = self._values.get("enabled_cloudwatch_logs_exports")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enable_global_write_forwarding(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#enable_global_write_forwarding RdsCluster#enable_global_write_forwarding}.'''
        result = self._values.get("enable_global_write_forwarding")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_http_endpoint(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#enable_http_endpoint RdsCluster#enable_http_endpoint}.'''
        result = self._values.get("enable_http_endpoint")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#engine RdsCluster#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#engine_mode RdsCluster#engine_mode}.'''
        result = self._values.get("engine_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#engine_version RdsCluster#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#final_snapshot_identifier RdsCluster#final_snapshot_identifier}.'''
        result = self._values.get("final_snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def global_cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#global_cluster_identifier RdsCluster#global_cluster_identifier}.'''
        result = self._values.get("global_cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_database_authentication_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#iam_database_authentication_enabled RdsCluster#iam_database_authentication_enabled}.'''
        result = self._values.get("iam_database_authentication_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iam_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#iam_roles RdsCluster#iam_roles}.'''
        result = self._values.get("iam_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#kms_key_id RdsCluster#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def master_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#master_password RdsCluster#master_password}.'''
        result = self._values.get("master_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def master_username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#master_username RdsCluster#master_username}.'''
        result = self._values.get("master_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#port RdsCluster#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_backup_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#preferred_backup_window RdsCluster#preferred_backup_window}.'''
        result = self._values.get("preferred_backup_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#preferred_maintenance_window RdsCluster#preferred_maintenance_window}.'''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_source_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#replication_source_identifier RdsCluster#replication_source_identifier}.'''
        result = self._values.get("replication_source_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restore_to_point_in_time(
        self,
    ) -> typing.Optional["RdsClusterRestoreToPointInTime"]:
        '''restore_to_point_in_time block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#restore_to_point_in_time RdsCluster#restore_to_point_in_time}
        '''
        result = self._values.get("restore_to_point_in_time")
        return typing.cast(typing.Optional["RdsClusterRestoreToPointInTime"], result)

    @builtins.property
    def s3_import(self) -> typing.Optional["RdsClusterS3Import"]:
        '''s3_import block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#s3_import RdsCluster#s3_import}
        '''
        result = self._values.get("s3_import")
        return typing.cast(typing.Optional["RdsClusterS3Import"], result)

    @builtins.property
    def scaling_configuration(
        self,
    ) -> typing.Optional["RdsClusterScalingConfiguration"]:
        '''scaling_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#scaling_configuration RdsCluster#scaling_configuration}
        '''
        result = self._values.get("scaling_configuration")
        return typing.cast(typing.Optional["RdsClusterScalingConfiguration"], result)

    @builtins.property
    def skip_final_snapshot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#skip_final_snapshot RdsCluster#skip_final_snapshot}.'''
        result = self._values.get("skip_final_snapshot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def snapshot_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#snapshot_identifier RdsCluster#snapshot_identifier}.'''
        result = self._values.get("snapshot_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_region RdsCluster#source_region}.'''
        result = self._values.get("source_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#storage_encrypted RdsCluster#storage_encrypted}.'''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#tags RdsCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#tags_all RdsCluster#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["RdsClusterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#timeouts RdsCluster#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["RdsClusterTimeouts"], result)

    @builtins.property
    def vpc_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#vpc_security_group_ids RdsCluster#vpc_security_group_ids}.'''
        result = self._values.get("vpc_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsClusterEndpoint(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsClusterEndpoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint aws_rds_cluster_endpoint}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_endpoint_identifier: builtins.str,
        cluster_identifier: builtins.str,
        custom_endpoint_type: builtins.str,
        excluded_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        static_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint aws_rds_cluster_endpoint} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_endpoint_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#cluster_endpoint_identifier RdsClusterEndpoint#cluster_endpoint_identifier}.
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#cluster_identifier RdsClusterEndpoint#cluster_identifier}.
        :param custom_endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#custom_endpoint_type RdsClusterEndpoint#custom_endpoint_type}.
        :param excluded_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#excluded_members RdsClusterEndpoint#excluded_members}.
        :param static_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#static_members RdsClusterEndpoint#static_members}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#tags RdsClusterEndpoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#tags_all RdsClusterEndpoint#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RdsClusterEndpointConfig(
            cluster_endpoint_identifier=cluster_endpoint_identifier,
            cluster_identifier=cluster_identifier,
            custom_endpoint_type=custom_endpoint_type,
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
    @jsii.member(jsii_name="customEndpointTypeInput")
    def custom_endpoint_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customEndpointTypeInput"))

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
    @jsii.member(jsii_name="customEndpointType")
    def custom_endpoint_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customEndpointType"))

    @custom_endpoint_type.setter
    def custom_endpoint_type(self, value: builtins.str) -> None:
        jsii.set(self, "customEndpointType", value)

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
    jsii_type="@cdktf/provider-aws.rds.RdsClusterEndpointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_endpoint_identifier": "clusterEndpointIdentifier",
        "cluster_identifier": "clusterIdentifier",
        "custom_endpoint_type": "customEndpointType",
        "excluded_members": "excludedMembers",
        "static_members": "staticMembers",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class RdsClusterEndpointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_endpoint_identifier: builtins.str,
        cluster_identifier: builtins.str,
        custom_endpoint_type: builtins.str,
        excluded_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        static_members: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_endpoint_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#cluster_endpoint_identifier RdsClusterEndpoint#cluster_endpoint_identifier}.
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#cluster_identifier RdsClusterEndpoint#cluster_identifier}.
        :param custom_endpoint_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#custom_endpoint_type RdsClusterEndpoint#custom_endpoint_type}.
        :param excluded_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#excluded_members RdsClusterEndpoint#excluded_members}.
        :param static_members: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#static_members RdsClusterEndpoint#static_members}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#tags RdsClusterEndpoint#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#tags_all RdsClusterEndpoint#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_endpoint_identifier": cluster_endpoint_identifier,
            "cluster_identifier": cluster_identifier,
            "custom_endpoint_type": custom_endpoint_type,
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#cluster_endpoint_identifier RdsClusterEndpoint#cluster_endpoint_identifier}.'''
        result = self._values.get("cluster_endpoint_identifier")
        assert result is not None, "Required property 'cluster_endpoint_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#cluster_identifier RdsClusterEndpoint#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_endpoint_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#custom_endpoint_type RdsClusterEndpoint#custom_endpoint_type}.'''
        result = self._values.get("custom_endpoint_type")
        assert result is not None, "Required property 'custom_endpoint_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def excluded_members(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#excluded_members RdsClusterEndpoint#excluded_members}.'''
        result = self._values.get("excluded_members")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def static_members(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#static_members RdsClusterEndpoint#static_members}.'''
        result = self._values.get("static_members")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#tags RdsClusterEndpoint#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_endpoint#tags_all RdsClusterEndpoint#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterEndpointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsClusterInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsClusterInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance aws_rds_cluster_instance}.'''

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
        ca_cert_identifier: typing.Optional[builtins.str] = None,
        copy_tags_to_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        db_parameter_group_name: typing.Optional[builtins.str] = None,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        identifier: typing.Optional[builtins.str] = None,
        identifier_prefix: typing.Optional[builtins.str] = None,
        monitoring_interval: typing.Optional[jsii.Number] = None,
        monitoring_role_arn: typing.Optional[builtins.str] = None,
        performance_insights_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        performance_insights_kms_key_id: typing.Optional[builtins.str] = None,
        performance_insights_retention_period: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        promotion_tier: typing.Optional[jsii.Number] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["RdsClusterInstanceTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance aws_rds_cluster_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#cluster_identifier RdsClusterInstance#cluster_identifier}.
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#instance_class RdsClusterInstance#instance_class}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#apply_immediately RdsClusterInstance#apply_immediately}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#auto_minor_version_upgrade RdsClusterInstance#auto_minor_version_upgrade}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#availability_zone RdsClusterInstance#availability_zone}.
        :param ca_cert_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#ca_cert_identifier RdsClusterInstance#ca_cert_identifier}.
        :param copy_tags_to_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#copy_tags_to_snapshot RdsClusterInstance#copy_tags_to_snapshot}.
        :param db_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#db_parameter_group_name RdsClusterInstance#db_parameter_group_name}.
        :param db_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#db_subnet_group_name RdsClusterInstance#db_subnet_group_name}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#engine RdsClusterInstance#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#engine_version RdsClusterInstance#engine_version}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#identifier RdsClusterInstance#identifier}.
        :param identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#identifier_prefix RdsClusterInstance#identifier_prefix}.
        :param monitoring_interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#monitoring_interval RdsClusterInstance#monitoring_interval}.
        :param monitoring_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#monitoring_role_arn RdsClusterInstance#monitoring_role_arn}.
        :param performance_insights_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#performance_insights_enabled RdsClusterInstance#performance_insights_enabled}.
        :param performance_insights_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#performance_insights_kms_key_id RdsClusterInstance#performance_insights_kms_key_id}.
        :param performance_insights_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#performance_insights_retention_period RdsClusterInstance#performance_insights_retention_period}.
        :param preferred_backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#preferred_backup_window RdsClusterInstance#preferred_backup_window}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#preferred_maintenance_window RdsClusterInstance#preferred_maintenance_window}.
        :param promotion_tier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#promotion_tier RdsClusterInstance#promotion_tier}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#publicly_accessible RdsClusterInstance#publicly_accessible}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#tags RdsClusterInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#tags_all RdsClusterInstance#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#timeouts RdsClusterInstance#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RdsClusterInstanceConfig(
            cluster_identifier=cluster_identifier,
            instance_class=instance_class,
            apply_immediately=apply_immediately,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            availability_zone=availability_zone,
            ca_cert_identifier=ca_cert_identifier,
            copy_tags_to_snapshot=copy_tags_to_snapshot,
            db_parameter_group_name=db_parameter_group_name,
            db_subnet_group_name=db_subnet_group_name,
            engine=engine,
            engine_version=engine_version,
            identifier=identifier,
            identifier_prefix=identifier_prefix,
            monitoring_interval=monitoring_interval,
            monitoring_role_arn=monitoring_role_arn,
            performance_insights_enabled=performance_insights_enabled,
            performance_insights_kms_key_id=performance_insights_kms_key_id,
            performance_insights_retention_period=performance_insights_retention_period,
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
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#create RdsClusterInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#delete RdsClusterInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#update RdsClusterInstance#update}.
        '''
        value = RdsClusterInstanceTimeouts(create=create, delete=delete, update=update)

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

    @jsii.member(jsii_name="resetCaCertIdentifier")
    def reset_ca_cert_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaCertIdentifier", []))

    @jsii.member(jsii_name="resetCopyTagsToSnapshot")
    def reset_copy_tags_to_snapshot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyTagsToSnapshot", []))

    @jsii.member(jsii_name="resetDbParameterGroupName")
    def reset_db_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbParameterGroupName", []))

    @jsii.member(jsii_name="resetDbSubnetGroupName")
    def reset_db_subnet_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbSubnetGroupName", []))

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

    @jsii.member(jsii_name="resetMonitoringInterval")
    def reset_monitoring_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMonitoringInterval", []))

    @jsii.member(jsii_name="resetMonitoringRoleArn")
    def reset_monitoring_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMonitoringRoleArn", []))

    @jsii.member(jsii_name="resetPerformanceInsightsEnabled")
    def reset_performance_insights_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerformanceInsightsEnabled", []))

    @jsii.member(jsii_name="resetPerformanceInsightsKmsKeyId")
    def reset_performance_insights_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerformanceInsightsKmsKeyId", []))

    @jsii.member(jsii_name="resetPerformanceInsightsRetentionPeriod")
    def reset_performance_insights_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPerformanceInsightsRetentionPeriod", []))

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
    @jsii.member(jsii_name="engineVersionActual")
    def engine_version_actual(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersionActual"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEncrypted")
    def storage_encrypted(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "storageEncrypted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "RdsClusterInstanceTimeoutsOutputReference":
        return typing.cast("RdsClusterInstanceTimeoutsOutputReference", jsii.get(self, "timeouts"))

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
    @jsii.member(jsii_name="caCertIdentifierInput")
    def ca_cert_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifierInput")
    def cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyTagsToSnapshotInput")
    def copy_tags_to_snapshot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "copyTagsToSnapshotInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbParameterGroupNameInput")
    def db_parameter_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbParameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupNameInput")
    def db_subnet_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbSubnetGroupNameInput"))

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
    @jsii.member(jsii_name="monitoringIntervalInput")
    def monitoring_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "monitoringIntervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitoringRoleArnInput")
    def monitoring_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "monitoringRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsEnabledInput")
    def performance_insights_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "performanceInsightsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsKmsKeyIdInput")
    def performance_insights_kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "performanceInsightsKmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsRetentionPeriodInput")
    def performance_insights_retention_period_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "performanceInsightsRetentionPeriodInput"))

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
    def timeouts_input(self) -> typing.Optional["RdsClusterInstanceTimeouts"]:
        return typing.cast(typing.Optional["RdsClusterInstanceTimeouts"], jsii.get(self, "timeoutsInput"))

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
    @jsii.member(jsii_name="caCertIdentifier")
    def ca_cert_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCertIdentifier"))

    @ca_cert_identifier.setter
    def ca_cert_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "caCertIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @cluster_identifier.setter
    def cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "clusterIdentifier", value)

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
    @jsii.member(jsii_name="dbParameterGroupName")
    def db_parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbParameterGroupName"))

    @db_parameter_group_name.setter
    def db_parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbParameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroupName")
    def db_subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbSubnetGroupName"))

    @db_subnet_group_name.setter
    def db_subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "dbSubnetGroupName", value)

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
    @jsii.member(jsii_name="monitoringInterval")
    def monitoring_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "monitoringInterval"))

    @monitoring_interval.setter
    def monitoring_interval(self, value: jsii.Number) -> None:
        jsii.set(self, "monitoringInterval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitoringRoleArn")
    def monitoring_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitoringRoleArn"))

    @monitoring_role_arn.setter
    def monitoring_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "monitoringRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsEnabled")
    def performance_insights_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "performanceInsightsEnabled"))

    @performance_insights_enabled.setter
    def performance_insights_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "performanceInsightsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsKmsKeyId")
    def performance_insights_kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "performanceInsightsKmsKeyId"))

    @performance_insights_kms_key_id.setter
    def performance_insights_kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "performanceInsightsKmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="performanceInsightsRetentionPeriod")
    def performance_insights_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "performanceInsightsRetentionPeriod"))

    @performance_insights_retention_period.setter
    def performance_insights_retention_period(self, value: jsii.Number) -> None:
        jsii.set(self, "performanceInsightsRetentionPeriod", value)

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
    jsii_type="@cdktf/provider-aws.rds.RdsClusterInstanceConfig",
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
        "ca_cert_identifier": "caCertIdentifier",
        "copy_tags_to_snapshot": "copyTagsToSnapshot",
        "db_parameter_group_name": "dbParameterGroupName",
        "db_subnet_group_name": "dbSubnetGroupName",
        "engine": "engine",
        "engine_version": "engineVersion",
        "identifier": "identifier",
        "identifier_prefix": "identifierPrefix",
        "monitoring_interval": "monitoringInterval",
        "monitoring_role_arn": "monitoringRoleArn",
        "performance_insights_enabled": "performanceInsightsEnabled",
        "performance_insights_kms_key_id": "performanceInsightsKmsKeyId",
        "performance_insights_retention_period": "performanceInsightsRetentionPeriod",
        "preferred_backup_window": "preferredBackupWindow",
        "preferred_maintenance_window": "preferredMaintenanceWindow",
        "promotion_tier": "promotionTier",
        "publicly_accessible": "publiclyAccessible",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class RdsClusterInstanceConfig(cdktf.TerraformMetaArguments):
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
        ca_cert_identifier: typing.Optional[builtins.str] = None,
        copy_tags_to_snapshot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        db_parameter_group_name: typing.Optional[builtins.str] = None,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        identifier: typing.Optional[builtins.str] = None,
        identifier_prefix: typing.Optional[builtins.str] = None,
        monitoring_interval: typing.Optional[jsii.Number] = None,
        monitoring_role_arn: typing.Optional[builtins.str] = None,
        performance_insights_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        performance_insights_kms_key_id: typing.Optional[builtins.str] = None,
        performance_insights_retention_period: typing.Optional[jsii.Number] = None,
        preferred_backup_window: typing.Optional[builtins.str] = None,
        preferred_maintenance_window: typing.Optional[builtins.str] = None,
        promotion_tier: typing.Optional[jsii.Number] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["RdsClusterInstanceTimeouts"] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#cluster_identifier RdsClusterInstance#cluster_identifier}.
        :param instance_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#instance_class RdsClusterInstance#instance_class}.
        :param apply_immediately: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#apply_immediately RdsClusterInstance#apply_immediately}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#auto_minor_version_upgrade RdsClusterInstance#auto_minor_version_upgrade}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#availability_zone RdsClusterInstance#availability_zone}.
        :param ca_cert_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#ca_cert_identifier RdsClusterInstance#ca_cert_identifier}.
        :param copy_tags_to_snapshot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#copy_tags_to_snapshot RdsClusterInstance#copy_tags_to_snapshot}.
        :param db_parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#db_parameter_group_name RdsClusterInstance#db_parameter_group_name}.
        :param db_subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#db_subnet_group_name RdsClusterInstance#db_subnet_group_name}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#engine RdsClusterInstance#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#engine_version RdsClusterInstance#engine_version}.
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#identifier RdsClusterInstance#identifier}.
        :param identifier_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#identifier_prefix RdsClusterInstance#identifier_prefix}.
        :param monitoring_interval: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#monitoring_interval RdsClusterInstance#monitoring_interval}.
        :param monitoring_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#monitoring_role_arn RdsClusterInstance#monitoring_role_arn}.
        :param performance_insights_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#performance_insights_enabled RdsClusterInstance#performance_insights_enabled}.
        :param performance_insights_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#performance_insights_kms_key_id RdsClusterInstance#performance_insights_kms_key_id}.
        :param performance_insights_retention_period: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#performance_insights_retention_period RdsClusterInstance#performance_insights_retention_period}.
        :param preferred_backup_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#preferred_backup_window RdsClusterInstance#preferred_backup_window}.
        :param preferred_maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#preferred_maintenance_window RdsClusterInstance#preferred_maintenance_window}.
        :param promotion_tier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#promotion_tier RdsClusterInstance#promotion_tier}.
        :param publicly_accessible: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#publicly_accessible RdsClusterInstance#publicly_accessible}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#tags RdsClusterInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#tags_all RdsClusterInstance#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#timeouts RdsClusterInstance#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = RdsClusterInstanceTimeouts(**timeouts)
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
        if ca_cert_identifier is not None:
            self._values["ca_cert_identifier"] = ca_cert_identifier
        if copy_tags_to_snapshot is not None:
            self._values["copy_tags_to_snapshot"] = copy_tags_to_snapshot
        if db_parameter_group_name is not None:
            self._values["db_parameter_group_name"] = db_parameter_group_name
        if db_subnet_group_name is not None:
            self._values["db_subnet_group_name"] = db_subnet_group_name
        if engine is not None:
            self._values["engine"] = engine
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if identifier is not None:
            self._values["identifier"] = identifier
        if identifier_prefix is not None:
            self._values["identifier_prefix"] = identifier_prefix
        if monitoring_interval is not None:
            self._values["monitoring_interval"] = monitoring_interval
        if monitoring_role_arn is not None:
            self._values["monitoring_role_arn"] = monitoring_role_arn
        if performance_insights_enabled is not None:
            self._values["performance_insights_enabled"] = performance_insights_enabled
        if performance_insights_kms_key_id is not None:
            self._values["performance_insights_kms_key_id"] = performance_insights_kms_key_id
        if performance_insights_retention_period is not None:
            self._values["performance_insights_retention_period"] = performance_insights_retention_period
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#cluster_identifier RdsClusterInstance#cluster_identifier}.'''
        result = self._values.get("cluster_identifier")
        assert result is not None, "Required property 'cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_class(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#instance_class RdsClusterInstance#instance_class}.'''
        result = self._values.get("instance_class")
        assert result is not None, "Required property 'instance_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def apply_immediately(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#apply_immediately RdsClusterInstance#apply_immediately}.'''
        result = self._values.get("apply_immediately")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#auto_minor_version_upgrade RdsClusterInstance#auto_minor_version_upgrade}.'''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#availability_zone RdsClusterInstance#availability_zone}.'''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_cert_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#ca_cert_identifier RdsClusterInstance#ca_cert_identifier}.'''
        result = self._values.get("ca_cert_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_tags_to_snapshot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#copy_tags_to_snapshot RdsClusterInstance#copy_tags_to_snapshot}.'''
        result = self._values.get("copy_tags_to_snapshot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def db_parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#db_parameter_group_name RdsClusterInstance#db_parameter_group_name}.'''
        result = self._values.get("db_parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#db_subnet_group_name RdsClusterInstance#db_subnet_group_name}.'''
        result = self._values.get("db_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#engine RdsClusterInstance#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#engine_version RdsClusterInstance#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#identifier RdsClusterInstance#identifier}.'''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identifier_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#identifier_prefix RdsClusterInstance#identifier_prefix}.'''
        result = self._values.get("identifier_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monitoring_interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#monitoring_interval RdsClusterInstance#monitoring_interval}.'''
        result = self._values.get("monitoring_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def monitoring_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#monitoring_role_arn RdsClusterInstance#monitoring_role_arn}.'''
        result = self._values.get("monitoring_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def performance_insights_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#performance_insights_enabled RdsClusterInstance#performance_insights_enabled}.'''
        result = self._values.get("performance_insights_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def performance_insights_kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#performance_insights_kms_key_id RdsClusterInstance#performance_insights_kms_key_id}.'''
        result = self._values.get("performance_insights_kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def performance_insights_retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#performance_insights_retention_period RdsClusterInstance#performance_insights_retention_period}.'''
        result = self._values.get("performance_insights_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_backup_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#preferred_backup_window RdsClusterInstance#preferred_backup_window}.'''
        result = self._values.get("preferred_backup_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preferred_maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#preferred_maintenance_window RdsClusterInstance#preferred_maintenance_window}.'''
        result = self._values.get("preferred_maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def promotion_tier(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#promotion_tier RdsClusterInstance#promotion_tier}.'''
        result = self._values.get("promotion_tier")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def publicly_accessible(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#publicly_accessible RdsClusterInstance#publicly_accessible}.'''
        result = self._values.get("publicly_accessible")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#tags RdsClusterInstance#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#tags_all RdsClusterInstance#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["RdsClusterInstanceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#timeouts RdsClusterInstance#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["RdsClusterInstanceTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.RdsClusterInstanceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class RdsClusterInstanceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#create RdsClusterInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#delete RdsClusterInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#update RdsClusterInstance#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#create RdsClusterInstance#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#delete RdsClusterInstance#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_instance#update RdsClusterInstance#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterInstanceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsClusterInstanceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsClusterInstanceTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[RdsClusterInstanceTimeouts]:
        return typing.cast(typing.Optional[RdsClusterInstanceTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RdsClusterInstanceTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class RdsClusterParameterGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsClusterParameterGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group aws_rds_cluster_parameter_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        family: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["RdsClusterParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group aws_rds_cluster_parameter_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#family RdsClusterParameterGroup#family}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#description RdsClusterParameterGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#name RdsClusterParameterGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#name_prefix RdsClusterParameterGroup#name_prefix}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#parameter RdsClusterParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#tags RdsClusterParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#tags_all RdsClusterParameterGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RdsClusterParameterGroupConfig(
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
    ) -> typing.Optional[typing.List["RdsClusterParameterGroupParameter"]]:
        return typing.cast(typing.Optional[typing.List["RdsClusterParameterGroupParameter"]], jsii.get(self, "parameterInput"))

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
    def parameter(self) -> typing.List["RdsClusterParameterGroupParameter"]:
        return typing.cast(typing.List["RdsClusterParameterGroupParameter"], jsii.get(self, "parameter"))

    @parameter.setter
    def parameter(
        self,
        value: typing.List["RdsClusterParameterGroupParameter"],
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
    jsii_type="@cdktf/provider-aws.rds.RdsClusterParameterGroupConfig",
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
class RdsClusterParameterGroupConfig(cdktf.TerraformMetaArguments):
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
        parameter: typing.Optional[typing.Sequence["RdsClusterParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#family RdsClusterParameterGroup#family}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#description RdsClusterParameterGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#name RdsClusterParameterGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#name_prefix RdsClusterParameterGroup#name_prefix}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#parameter RdsClusterParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#tags RdsClusterParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#tags_all RdsClusterParameterGroup#tags_all}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#family RdsClusterParameterGroup#family}.'''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#description RdsClusterParameterGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#name RdsClusterParameterGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#name_prefix RdsClusterParameterGroup#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.List["RdsClusterParameterGroupParameter"]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#parameter RdsClusterParameterGroup#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.List["RdsClusterParameterGroupParameter"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#tags RdsClusterParameterGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#tags_all RdsClusterParameterGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterParameterGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.RdsClusterParameterGroupParameter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value", "apply_method": "applyMethod"},
)
class RdsClusterParameterGroupParameter:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: builtins.str,
        apply_method: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#name RdsClusterParameterGroup#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#value RdsClusterParameterGroup#value}.
        :param apply_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#apply_method RdsClusterParameterGroup#apply_method}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }
        if apply_method is not None:
            self._values["apply_method"] = apply_method

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#name RdsClusterParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#value RdsClusterParameterGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def apply_method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_parameter_group#apply_method RdsClusterParameterGroup#apply_method}.'''
        result = self._values.get("apply_method")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterParameterGroupParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.RdsClusterRestoreToPointInTime",
    jsii_struct_bases=[],
    name_mapping={
        "source_cluster_identifier": "sourceClusterIdentifier",
        "restore_to_time": "restoreToTime",
        "restore_type": "restoreType",
        "use_latest_restorable_time": "useLatestRestorableTime",
    },
)
class RdsClusterRestoreToPointInTime:
    def __init__(
        self,
        *,
        source_cluster_identifier: builtins.str,
        restore_to_time: typing.Optional[builtins.str] = None,
        restore_type: typing.Optional[builtins.str] = None,
        use_latest_restorable_time: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param source_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_cluster_identifier RdsCluster#source_cluster_identifier}.
        :param restore_to_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#restore_to_time RdsCluster#restore_to_time}.
        :param restore_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#restore_type RdsCluster#restore_type}.
        :param use_latest_restorable_time: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#use_latest_restorable_time RdsCluster#use_latest_restorable_time}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "source_cluster_identifier": source_cluster_identifier,
        }
        if restore_to_time is not None:
            self._values["restore_to_time"] = restore_to_time
        if restore_type is not None:
            self._values["restore_type"] = restore_type
        if use_latest_restorable_time is not None:
            self._values["use_latest_restorable_time"] = use_latest_restorable_time

    @builtins.property
    def source_cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_cluster_identifier RdsCluster#source_cluster_identifier}.'''
        result = self._values.get("source_cluster_identifier")
        assert result is not None, "Required property 'source_cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def restore_to_time(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#restore_to_time RdsCluster#restore_to_time}.'''
        result = self._values.get("restore_to_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restore_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#restore_type RdsCluster#restore_type}.'''
        result = self._values.get("restore_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_latest_restorable_time(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#use_latest_restorable_time RdsCluster#use_latest_restorable_time}.'''
        result = self._values.get("use_latest_restorable_time")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterRestoreToPointInTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsClusterRestoreToPointInTimeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsClusterRestoreToPointInTimeOutputReference",
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

    @jsii.member(jsii_name="resetRestoreToTime")
    def reset_restore_to_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreToTime", []))

    @jsii.member(jsii_name="resetRestoreType")
    def reset_restore_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreType", []))

    @jsii.member(jsii_name="resetUseLatestRestorableTime")
    def reset_use_latest_restorable_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseLatestRestorableTime", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreToTimeInput")
    def restore_to_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restoreToTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreTypeInput")
    def restore_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restoreTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceClusterIdentifierInput")
    def source_cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceClusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useLatestRestorableTimeInput")
    def use_latest_restorable_time_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useLatestRestorableTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreToTime")
    def restore_to_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restoreToTime"))

    @restore_to_time.setter
    def restore_to_time(self, value: builtins.str) -> None:
        jsii.set(self, "restoreToTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restoreType")
    def restore_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restoreType"))

    @restore_type.setter
    def restore_type(self, value: builtins.str) -> None:
        jsii.set(self, "restoreType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceClusterIdentifier")
    def source_cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceClusterIdentifier"))

    @source_cluster_identifier.setter
    def source_cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "sourceClusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useLatestRestorableTime")
    def use_latest_restorable_time(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useLatestRestorableTime"))

    @use_latest_restorable_time.setter
    def use_latest_restorable_time(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useLatestRestorableTime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RdsClusterRestoreToPointInTime]:
        return typing.cast(typing.Optional[RdsClusterRestoreToPointInTime], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RdsClusterRestoreToPointInTime],
    ) -> None:
        jsii.set(self, "internalValue", value)


class RdsClusterRoleAssociation(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsClusterRoleAssociation",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association aws_rds_cluster_role_association}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_cluster_identifier: builtins.str,
        feature_name: builtins.str,
        role_arn: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association aws_rds_cluster_role_association} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association#db_cluster_identifier RdsClusterRoleAssociation#db_cluster_identifier}.
        :param feature_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association#feature_name RdsClusterRoleAssociation#feature_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association#role_arn RdsClusterRoleAssociation#role_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RdsClusterRoleAssociationConfig(
            db_cluster_identifier=db_cluster_identifier,
            feature_name=feature_name,
            role_arn=role_arn,
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
    @jsii.member(jsii_name="dbClusterIdentifierInput")
    def db_cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbClusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureNameInput")
    def feature_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "featureNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbClusterIdentifier"))

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "dbClusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureName")
    def feature_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "featureName"))

    @feature_name.setter
    def feature_name(self, value: builtins.str) -> None:
        jsii.set(self, "featureName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.RdsClusterRoleAssociationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_cluster_identifier": "dbClusterIdentifier",
        "feature_name": "featureName",
        "role_arn": "roleArn",
    },
)
class RdsClusterRoleAssociationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_cluster_identifier: builtins.str,
        feature_name: builtins.str,
        role_arn: builtins.str,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association#db_cluster_identifier RdsClusterRoleAssociation#db_cluster_identifier}.
        :param feature_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association#feature_name RdsClusterRoleAssociation#feature_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association#role_arn RdsClusterRoleAssociation#role_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "db_cluster_identifier": db_cluster_identifier,
            "feature_name": feature_name,
            "role_arn": role_arn,
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
    def db_cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association#db_cluster_identifier RdsClusterRoleAssociation#db_cluster_identifier}.'''
        result = self._values.get("db_cluster_identifier")
        assert result is not None, "Required property 'db_cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def feature_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association#feature_name RdsClusterRoleAssociation#feature_name}.'''
        result = self._values.get("feature_name")
        assert result is not None, "Required property 'feature_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster_role_association#role_arn RdsClusterRoleAssociation#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterRoleAssociationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.RdsClusterS3Import",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "ingestion_role": "ingestionRole",
        "source_engine": "sourceEngine",
        "source_engine_version": "sourceEngineVersion",
        "bucket_prefix": "bucketPrefix",
    },
)
class RdsClusterS3Import:
    def __init__(
        self,
        *,
        bucket_name: builtins.str,
        ingestion_role: builtins.str,
        source_engine: builtins.str,
        source_engine_version: builtins.str,
        bucket_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#bucket_name RdsCluster#bucket_name}.
        :param ingestion_role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#ingestion_role RdsCluster#ingestion_role}.
        :param source_engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_engine RdsCluster#source_engine}.
        :param source_engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_engine_version RdsCluster#source_engine_version}.
        :param bucket_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#bucket_prefix RdsCluster#bucket_prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
            "ingestion_role": ingestion_role,
            "source_engine": source_engine,
            "source_engine_version": source_engine_version,
        }
        if bucket_prefix is not None:
            self._values["bucket_prefix"] = bucket_prefix

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#bucket_name RdsCluster#bucket_name}.'''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ingestion_role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#ingestion_role RdsCluster#ingestion_role}.'''
        result = self._values.get("ingestion_role")
        assert result is not None, "Required property 'ingestion_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_engine(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_engine RdsCluster#source_engine}.'''
        result = self._values.get("source_engine")
        assert result is not None, "Required property 'source_engine' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_engine_version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#source_engine_version RdsCluster#source_engine_version}.'''
        result = self._values.get("source_engine_version")
        assert result is not None, "Required property 'source_engine_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#bucket_prefix RdsCluster#bucket_prefix}.'''
        result = self._values.get("bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterS3Import(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsClusterS3ImportOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsClusterS3ImportOutputReference",
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

    @jsii.member(jsii_name="resetBucketPrefix")
    def reset_bucket_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketPrefixInput")
    def bucket_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingestionRoleInput")
    def ingestion_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ingestionRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEngineInput")
    def source_engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceEngineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEngineVersionInput")
    def source_engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceEngineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "bucketName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketPrefix")
    def bucket_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketPrefix"))

    @bucket_prefix.setter
    def bucket_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "bucketPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingestionRole")
    def ingestion_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ingestionRole"))

    @ingestion_role.setter
    def ingestion_role(self, value: builtins.str) -> None:
        jsii.set(self, "ingestionRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEngine")
    def source_engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceEngine"))

    @source_engine.setter
    def source_engine(self, value: builtins.str) -> None:
        jsii.set(self, "sourceEngine", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceEngineVersion")
    def source_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceEngineVersion"))

    @source_engine_version.setter
    def source_engine_version(self, value: builtins.str) -> None:
        jsii.set(self, "sourceEngineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RdsClusterS3Import]:
        return typing.cast(typing.Optional[RdsClusterS3Import], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[RdsClusterS3Import]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.RdsClusterScalingConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "auto_pause": "autoPause",
        "max_capacity": "maxCapacity",
        "min_capacity": "minCapacity",
        "seconds_until_auto_pause": "secondsUntilAutoPause",
        "timeout_action": "timeoutAction",
    },
)
class RdsClusterScalingConfiguration:
    def __init__(
        self,
        *,
        auto_pause: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        seconds_until_auto_pause: typing.Optional[jsii.Number] = None,
        timeout_action: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auto_pause: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#auto_pause RdsCluster#auto_pause}.
        :param max_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#max_capacity RdsCluster#max_capacity}.
        :param min_capacity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#min_capacity RdsCluster#min_capacity}.
        :param seconds_until_auto_pause: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#seconds_until_auto_pause RdsCluster#seconds_until_auto_pause}.
        :param timeout_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#timeout_action RdsCluster#timeout_action}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if auto_pause is not None:
            self._values["auto_pause"] = auto_pause
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if min_capacity is not None:
            self._values["min_capacity"] = min_capacity
        if seconds_until_auto_pause is not None:
            self._values["seconds_until_auto_pause"] = seconds_until_auto_pause
        if timeout_action is not None:
            self._values["timeout_action"] = timeout_action

    @builtins.property
    def auto_pause(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#auto_pause RdsCluster#auto_pause}.'''
        result = self._values.get("auto_pause")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#max_capacity RdsCluster#max_capacity}.'''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_capacity(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#min_capacity RdsCluster#min_capacity}.'''
        result = self._values.get("min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def seconds_until_auto_pause(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#seconds_until_auto_pause RdsCluster#seconds_until_auto_pause}.'''
        result = self._values.get("seconds_until_auto_pause")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout_action(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#timeout_action RdsCluster#timeout_action}.'''
        result = self._values.get("timeout_action")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterScalingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsClusterScalingConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsClusterScalingConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetAutoPause")
    def reset_auto_pause(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoPause", []))

    @jsii.member(jsii_name="resetMaxCapacity")
    def reset_max_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCapacity", []))

    @jsii.member(jsii_name="resetMinCapacity")
    def reset_min_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinCapacity", []))

    @jsii.member(jsii_name="resetSecondsUntilAutoPause")
    def reset_seconds_until_auto_pause(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondsUntilAutoPause", []))

    @jsii.member(jsii_name="resetTimeoutAction")
    def reset_timeout_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutAction", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoPauseInput")
    def auto_pause_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoPauseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxCapacityInput")
    def max_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minCapacityInput")
    def min_capacity_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minCapacityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondsUntilAutoPauseInput")
    def seconds_until_auto_pause_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "secondsUntilAutoPauseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutActionInput")
    def timeout_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeoutActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoPause")
    def auto_pause(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoPause"))

    @auto_pause.setter
    def auto_pause(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "autoPause", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxCapacity")
    def max_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCapacity"))

    @max_capacity.setter
    def max_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "maxCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minCapacity")
    def min_capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minCapacity"))

    @min_capacity.setter
    def min_capacity(self, value: jsii.Number) -> None:
        jsii.set(self, "minCapacity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secondsUntilAutoPause")
    def seconds_until_auto_pause(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "secondsUntilAutoPause"))

    @seconds_until_auto_pause.setter
    def seconds_until_auto_pause(self, value: jsii.Number) -> None:
        jsii.set(self, "secondsUntilAutoPause", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutAction")
    def timeout_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeoutAction"))

    @timeout_action.setter
    def timeout_action(self, value: builtins.str) -> None:
        jsii.set(self, "timeoutAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RdsClusterScalingConfiguration]:
        return typing.cast(typing.Optional[RdsClusterScalingConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RdsClusterScalingConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.RdsClusterTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class RdsClusterTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#create RdsCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#delete RdsCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#update RdsCluster#update}.
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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#create RdsCluster#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#delete RdsCluster#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_cluster#update RdsCluster#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsClusterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsClusterTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsClusterTimeoutsOutputReference",
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
    def internal_value(self) -> typing.Optional[RdsClusterTimeouts]:
        return typing.cast(typing.Optional[RdsClusterTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[RdsClusterTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class RdsGlobalCluster(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsGlobalCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster aws_rds_global_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        global_cluster_identifier: builtins.str,
        database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        source_db_cluster_identifier: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster aws_rds_global_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param global_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#global_cluster_identifier RdsGlobalCluster#global_cluster_identifier}.
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#database_name RdsGlobalCluster#database_name}.
        :param deletion_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#deletion_protection RdsGlobalCluster#deletion_protection}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#engine RdsGlobalCluster#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#engine_version RdsGlobalCluster#engine_version}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#force_destroy RdsGlobalCluster#force_destroy}.
        :param source_db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#source_db_cluster_identifier RdsGlobalCluster#source_db_cluster_identifier}.
        :param storage_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#storage_encrypted RdsGlobalCluster#storage_encrypted}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RdsGlobalClusterConfig(
            global_cluster_identifier=global_cluster_identifier,
            database_name=database_name,
            deletion_protection=deletion_protection,
            engine=engine,
            engine_version=engine_version,
            force_destroy=force_destroy,
            source_db_cluster_identifier=source_db_cluster_identifier,
            storage_encrypted=storage_encrypted,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="globalClusterMembers")
    def global_cluster_members(
        self,
        index: builtins.str,
    ) -> "RdsGlobalClusterGlobalClusterMembers":
        '''
        :param index: -
        '''
        return typing.cast("RdsGlobalClusterGlobalClusterMembers", jsii.invoke(self, "globalClusterMembers", [index]))

    @jsii.member(jsii_name="resetDatabaseName")
    def reset_database_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseName", []))

    @jsii.member(jsii_name="resetDeletionProtection")
    def reset_deletion_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletionProtection", []))

    @jsii.member(jsii_name="resetEngine")
    def reset_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngine", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetSourceDbClusterIdentifier")
    def reset_source_db_cluster_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceDbClusterIdentifier", []))

    @jsii.member(jsii_name="resetStorageEncrypted")
    def reset_storage_encrypted(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageEncrypted", []))

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
    @jsii.member(jsii_name="globalClusterResourceId")
    def global_cluster_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalClusterResourceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseNameInput")
    def database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deletionProtectionInput")
    def deletion_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deletionProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineInput")
    def engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionInput")
    def engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalClusterIdentifierInput")
    def global_cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "globalClusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDbClusterIdentifierInput")
    def source_db_cluster_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceDbClusterIdentifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageEncryptedInput")
    def storage_encrypted_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "storageEncryptedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="databaseName")
    def database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseName"))

    @database_name.setter
    def database_name(self, value: builtins.str) -> None:
        jsii.set(self, "databaseName", value)

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
    @jsii.member(jsii_name="globalClusterIdentifier")
    def global_cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalClusterIdentifier"))

    @global_cluster_identifier.setter
    def global_cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "globalClusterIdentifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDbClusterIdentifier")
    def source_db_cluster_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDbClusterIdentifier"))

    @source_db_cluster_identifier.setter
    def source_db_cluster_identifier(self, value: builtins.str) -> None:
        jsii.set(self, "sourceDbClusterIdentifier", value)

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


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.rds.RdsGlobalClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "global_cluster_identifier": "globalClusterIdentifier",
        "database_name": "databaseName",
        "deletion_protection": "deletionProtection",
        "engine": "engine",
        "engine_version": "engineVersion",
        "force_destroy": "forceDestroy",
        "source_db_cluster_identifier": "sourceDbClusterIdentifier",
        "storage_encrypted": "storageEncrypted",
    },
)
class RdsGlobalClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        global_cluster_identifier: builtins.str,
        database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        engine: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        source_db_cluster_identifier: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Relational Database Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param global_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#global_cluster_identifier RdsGlobalCluster#global_cluster_identifier}.
        :param database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#database_name RdsGlobalCluster#database_name}.
        :param deletion_protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#deletion_protection RdsGlobalCluster#deletion_protection}.
        :param engine: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#engine RdsGlobalCluster#engine}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#engine_version RdsGlobalCluster#engine_version}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#force_destroy RdsGlobalCluster#force_destroy}.
        :param source_db_cluster_identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#source_db_cluster_identifier RdsGlobalCluster#source_db_cluster_identifier}.
        :param storage_encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#storage_encrypted RdsGlobalCluster#storage_encrypted}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "global_cluster_identifier": global_cluster_identifier,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if database_name is not None:
            self._values["database_name"] = database_name
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if engine is not None:
            self._values["engine"] = engine
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if source_db_cluster_identifier is not None:
            self._values["source_db_cluster_identifier"] = source_db_cluster_identifier
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted

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
    def global_cluster_identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#global_cluster_identifier RdsGlobalCluster#global_cluster_identifier}.'''
        result = self._values.get("global_cluster_identifier")
        assert result is not None, "Required property 'global_cluster_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#database_name RdsGlobalCluster#database_name}.'''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deletion_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#deletion_protection RdsGlobalCluster#deletion_protection}.'''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#engine RdsGlobalCluster#engine}.'''
        result = self._values.get("engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#engine_version RdsGlobalCluster#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#force_destroy RdsGlobalCluster#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def source_db_cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#source_db_cluster_identifier RdsGlobalCluster#source_db_cluster_identifier}.'''
        result = self._values.get("source_db_cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/rds_global_cluster#storage_encrypted RdsGlobalCluster#storage_encrypted}.'''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsGlobalClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsGlobalClusterGlobalClusterMembers(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.rds.RdsGlobalClusterGlobalClusterMembers",
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
    @jsii.member(jsii_name="dbClusterArn")
    def db_cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbClusterArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isWriter")
    def is_writer(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "isWriter"))


__all__ = [
    "DataAwsDbClusterSnapshot",
    "DataAwsDbClusterSnapshotConfig",
    "DataAwsDbEventCategories",
    "DataAwsDbEventCategoriesConfig",
    "DataAwsDbInstance",
    "DataAwsDbInstanceConfig",
    "DataAwsDbProxy",
    "DataAwsDbProxyAuth",
    "DataAwsDbProxyConfig",
    "DataAwsDbSnapshot",
    "DataAwsDbSnapshotConfig",
    "DataAwsDbSubnetGroup",
    "DataAwsDbSubnetGroupConfig",
    "DataAwsRdsCertificate",
    "DataAwsRdsCertificateConfig",
    "DataAwsRdsCluster",
    "DataAwsRdsClusterConfig",
    "DataAwsRdsEngineVersion",
    "DataAwsRdsEngineVersionConfig",
    "DataAwsRdsOrderableDbInstance",
    "DataAwsRdsOrderableDbInstanceConfig",
    "DbClusterSnapshot",
    "DbClusterSnapshotConfig",
    "DbClusterSnapshotTimeouts",
    "DbClusterSnapshotTimeoutsOutputReference",
    "DbEventSubscription",
    "DbEventSubscriptionConfig",
    "DbEventSubscriptionTimeouts",
    "DbEventSubscriptionTimeoutsOutputReference",
    "DbInstance",
    "DbInstanceConfig",
    "DbInstanceRestoreToPointInTime",
    "DbInstanceRestoreToPointInTimeOutputReference",
    "DbInstanceRoleAssociation",
    "DbInstanceRoleAssociationConfig",
    "DbInstanceS3Import",
    "DbInstanceS3ImportOutputReference",
    "DbInstanceTimeouts",
    "DbInstanceTimeoutsOutputReference",
    "DbOptionGroup",
    "DbOptionGroupConfig",
    "DbOptionGroupOption",
    "DbOptionGroupOptionOptionSettings",
    "DbOptionGroupTimeouts",
    "DbOptionGroupTimeoutsOutputReference",
    "DbParameterGroup",
    "DbParameterGroupConfig",
    "DbParameterGroupParameter",
    "DbProxy",
    "DbProxyAuth",
    "DbProxyConfig",
    "DbProxyDefaultTargetGroup",
    "DbProxyDefaultTargetGroupConfig",
    "DbProxyDefaultTargetGroupConnectionPoolConfig",
    "DbProxyDefaultTargetGroupConnectionPoolConfigOutputReference",
    "DbProxyDefaultTargetGroupTimeouts",
    "DbProxyDefaultTargetGroupTimeoutsOutputReference",
    "DbProxyEndpoint",
    "DbProxyEndpointConfig",
    "DbProxyEndpointTimeouts",
    "DbProxyEndpointTimeoutsOutputReference",
    "DbProxyTarget",
    "DbProxyTargetConfig",
    "DbProxyTimeouts",
    "DbProxyTimeoutsOutputReference",
    "DbSecurityGroup",
    "DbSecurityGroupConfig",
    "DbSecurityGroupIngress",
    "DbSnapshot",
    "DbSnapshotConfig",
    "DbSnapshotTimeouts",
    "DbSnapshotTimeoutsOutputReference",
    "DbSubnetGroup",
    "DbSubnetGroupConfig",
    "RdsCluster",
    "RdsClusterConfig",
    "RdsClusterEndpoint",
    "RdsClusterEndpointConfig",
    "RdsClusterInstance",
    "RdsClusterInstanceConfig",
    "RdsClusterInstanceTimeouts",
    "RdsClusterInstanceTimeoutsOutputReference",
    "RdsClusterParameterGroup",
    "RdsClusterParameterGroupConfig",
    "RdsClusterParameterGroupParameter",
    "RdsClusterRestoreToPointInTime",
    "RdsClusterRestoreToPointInTimeOutputReference",
    "RdsClusterRoleAssociation",
    "RdsClusterRoleAssociationConfig",
    "RdsClusterS3Import",
    "RdsClusterS3ImportOutputReference",
    "RdsClusterScalingConfiguration",
    "RdsClusterScalingConfigurationOutputReference",
    "RdsClusterTimeouts",
    "RdsClusterTimeoutsOutputReference",
    "RdsGlobalCluster",
    "RdsGlobalClusterConfig",
    "RdsGlobalClusterGlobalClusterMembers",
]

publication.publish()
