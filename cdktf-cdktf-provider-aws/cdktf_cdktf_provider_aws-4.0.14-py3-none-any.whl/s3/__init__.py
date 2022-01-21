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


class DataAwsS3Bucket(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.DataAwsS3Bucket",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket aws_s3_bucket}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket aws_s3_bucket} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket#bucket DataAwsS3Bucket#bucket}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsS3BucketConfig(
            bucket=bucket,
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
    @jsii.member(jsii_name="bucketDomainName")
    def bucket_domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketRegionalDomainName")
    def bucket_regional_domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketRegionalDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="websiteDomain")
    def website_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "websiteDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="websiteEndpoint")
    def website_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "websiteEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.DataAwsS3BucketConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
    },
)
class DataAwsS3BucketConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket#bucket DataAwsS3Bucket#bucket}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket#bucket DataAwsS3Bucket#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsS3BucketConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsS3BucketObject(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.DataAwsS3BucketObject",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object aws_s3_bucket_object}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        key: builtins.str,
        range: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        version_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object aws_s3_bucket_object} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#bucket DataAwsS3BucketObject#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#key DataAwsS3BucketObject#key}.
        :param range: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#range DataAwsS3BucketObject#range}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#tags DataAwsS3BucketObject#tags}.
        :param version_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#version_id DataAwsS3BucketObject#version_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsS3BucketObjectConfig(
            bucket=bucket,
            key=key,
            range=range,
            tags=tags,
            version_id=version_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="metadata")
    def metadata(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "metadata", [key]))

    @jsii.member(jsii_name="resetRange")
    def reset_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRange", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetVersionId")
    def reset_version_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersionId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="body")
    def body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "body"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketKeyEnabled")
    def bucket_key_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "bucketKeyEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheControl")
    def cache_control(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheControl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentDisposition")
    def content_disposition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentDisposition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentEncoding")
    def content_encoding(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentEncoding"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentLanguage")
    def content_language(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentLanguage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentLength")
    def content_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "contentLength"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expiration")
    def expiration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expires")
    def expires(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expires"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModified"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockLegalHoldStatus")
    def object_lock_legal_hold_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockLegalHoldStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockMode")
    def object_lock_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockMode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockRetainUntilDate")
    def object_lock_retain_until_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockRetainUntilDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryption")
    def server_side_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverSideEncryption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseKmsKeyId")
    def sse_kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sseKmsKeyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClass")
    def storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageClass"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="websiteRedirectLocation")
    def website_redirect_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "websiteRedirectLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeInput")
    def range_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionIdInput")
    def version_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="range")
    def range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "range"))

    @range.setter
    def range(self, value: builtins.str) -> None:
        jsii.set(self, "range", value)

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
    @jsii.member(jsii_name="versionId")
    def version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionId"))

    @version_id.setter
    def version_id(self, value: builtins.str) -> None:
        jsii.set(self, "versionId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.DataAwsS3BucketObjectConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "key": "key",
        "range": "range",
        "tags": "tags",
        "version_id": "versionId",
    },
)
class DataAwsS3BucketObjectConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        key: builtins.str,
        range: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        version_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#bucket DataAwsS3BucketObject#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#key DataAwsS3BucketObject#key}.
        :param range: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#range DataAwsS3BucketObject#range}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#tags DataAwsS3BucketObject#tags}.
        :param version_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#version_id DataAwsS3BucketObject#version_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "key": key,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if range is not None:
            self._values["range"] = range
        if tags is not None:
            self._values["tags"] = tags
        if version_id is not None:
            self._values["version_id"] = version_id

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#bucket DataAwsS3BucketObject#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#key DataAwsS3BucketObject#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def range(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#range DataAwsS3BucketObject#range}.'''
        result = self._values.get("range")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#tags DataAwsS3BucketObject#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def version_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_object#version_id DataAwsS3BucketObject#version_id}.'''
        result = self._values.get("version_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsS3BucketObjectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsS3BucketObjects(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.DataAwsS3BucketObjects",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects aws_s3_bucket_objects}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        delimiter: typing.Optional[builtins.str] = None,
        encoding_type: typing.Optional[builtins.str] = None,
        fetch_owner: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_keys: typing.Optional[jsii.Number] = None,
        prefix: typing.Optional[builtins.str] = None,
        start_after: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects aws_s3_bucket_objects} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#bucket DataAwsS3BucketObjects#bucket}.
        :param delimiter: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#delimiter DataAwsS3BucketObjects#delimiter}.
        :param encoding_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#encoding_type DataAwsS3BucketObjects#encoding_type}.
        :param fetch_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#fetch_owner DataAwsS3BucketObjects#fetch_owner}.
        :param max_keys: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#max_keys DataAwsS3BucketObjects#max_keys}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#prefix DataAwsS3BucketObjects#prefix}.
        :param start_after: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#start_after DataAwsS3BucketObjects#start_after}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsS3BucketObjectsConfig(
            bucket=bucket,
            delimiter=delimiter,
            encoding_type=encoding_type,
            fetch_owner=fetch_owner,
            max_keys=max_keys,
            prefix=prefix,
            start_after=start_after,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDelimiter")
    def reset_delimiter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelimiter", []))

    @jsii.member(jsii_name="resetEncodingType")
    def reset_encoding_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncodingType", []))

    @jsii.member(jsii_name="resetFetchOwner")
    def reset_fetch_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFetchOwner", []))

    @jsii.member(jsii_name="resetMaxKeys")
    def reset_max_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxKeys", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetStartAfter")
    def reset_start_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartAfter", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commonPrefixes")
    def common_prefixes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "commonPrefixes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keys")
    def keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "keys"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owners")
    def owners(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "owners"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delimiterInput")
    def delimiter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "delimiterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encodingTypeInput")
    def encoding_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encodingTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fetchOwnerInput")
    def fetch_owner_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "fetchOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxKeysInput")
    def max_keys_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxKeysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startAfterInput")
    def start_after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startAfterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delimiter")
    def delimiter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delimiter"))

    @delimiter.setter
    def delimiter(self, value: builtins.str) -> None:
        jsii.set(self, "delimiter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encodingType")
    def encoding_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encodingType"))

    @encoding_type.setter
    def encoding_type(self, value: builtins.str) -> None:
        jsii.set(self, "encodingType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fetchOwner")
    def fetch_owner(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "fetchOwner"))

    @fetch_owner.setter
    def fetch_owner(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "fetchOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxKeys")
    def max_keys(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxKeys"))

    @max_keys.setter
    def max_keys(self, value: jsii.Number) -> None:
        jsii.set(self, "maxKeys", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startAfter")
    def start_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startAfter"))

    @start_after.setter
    def start_after(self, value: builtins.str) -> None:
        jsii.set(self, "startAfter", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.DataAwsS3BucketObjectsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "delimiter": "delimiter",
        "encoding_type": "encodingType",
        "fetch_owner": "fetchOwner",
        "max_keys": "maxKeys",
        "prefix": "prefix",
        "start_after": "startAfter",
    },
)
class DataAwsS3BucketObjectsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        delimiter: typing.Optional[builtins.str] = None,
        encoding_type: typing.Optional[builtins.str] = None,
        fetch_owner: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_keys: typing.Optional[jsii.Number] = None,
        prefix: typing.Optional[builtins.str] = None,
        start_after: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#bucket DataAwsS3BucketObjects#bucket}.
        :param delimiter: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#delimiter DataAwsS3BucketObjects#delimiter}.
        :param encoding_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#encoding_type DataAwsS3BucketObjects#encoding_type}.
        :param fetch_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#fetch_owner DataAwsS3BucketObjects#fetch_owner}.
        :param max_keys: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#max_keys DataAwsS3BucketObjects#max_keys}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#prefix DataAwsS3BucketObjects#prefix}.
        :param start_after: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#start_after DataAwsS3BucketObjects#start_after}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if delimiter is not None:
            self._values["delimiter"] = delimiter
        if encoding_type is not None:
            self._values["encoding_type"] = encoding_type
        if fetch_owner is not None:
            self._values["fetch_owner"] = fetch_owner
        if max_keys is not None:
            self._values["max_keys"] = max_keys
        if prefix is not None:
            self._values["prefix"] = prefix
        if start_after is not None:
            self._values["start_after"] = start_after

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#bucket DataAwsS3BucketObjects#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delimiter(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#delimiter DataAwsS3BucketObjects#delimiter}.'''
        result = self._values.get("delimiter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encoding_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#encoding_type DataAwsS3BucketObjects#encoding_type}.'''
        result = self._values.get("encoding_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fetch_owner(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#fetch_owner DataAwsS3BucketObjects#fetch_owner}.'''
        result = self._values.get("fetch_owner")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def max_keys(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#max_keys DataAwsS3BucketObjects#max_keys}.'''
        result = self._values.get("max_keys")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#prefix DataAwsS3BucketObjects#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_after(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/s3_bucket_objects#start_after DataAwsS3BucketObjects#start_after}.'''
        result = self._values.get("start_after")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsS3BucketObjectsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3AccessPoint(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3AccessPoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point aws_s3_access_point}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        public_access_block_configuration: typing.Optional["S3AccessPointPublicAccessBlockConfiguration"] = None,
        vpc_configuration: typing.Optional["S3AccessPointVpcConfiguration"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point aws_s3_access_point} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#bucket S3AccessPoint#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#name S3AccessPoint#name}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#account_id S3AccessPoint#account_id}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#policy S3AccessPoint#policy}.
        :param public_access_block_configuration: public_access_block_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#public_access_block_configuration S3AccessPoint#public_access_block_configuration}
        :param vpc_configuration: vpc_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#vpc_configuration S3AccessPoint#vpc_configuration}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3AccessPointConfig(
            bucket=bucket,
            name=name,
            account_id=account_id,
            policy=policy,
            public_access_block_configuration=public_access_block_configuration,
            vpc_configuration=vpc_configuration,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="endpoints")
    def endpoints(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "endpoints", [key]))

    @jsii.member(jsii_name="putPublicAccessBlockConfiguration")
    def put_public_access_block_configuration(
        self,
        *,
        block_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restrict_public_buckets: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param block_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#block_public_acls S3AccessPoint#block_public_acls}.
        :param block_public_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#block_public_policy S3AccessPoint#block_public_policy}.
        :param ignore_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#ignore_public_acls S3AccessPoint#ignore_public_acls}.
        :param restrict_public_buckets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#restrict_public_buckets S3AccessPoint#restrict_public_buckets}.
        '''
        value = S3AccessPointPublicAccessBlockConfiguration(
            block_public_acls=block_public_acls,
            block_public_policy=block_public_policy,
            ignore_public_acls=ignore_public_acls,
            restrict_public_buckets=restrict_public_buckets,
        )

        return typing.cast(None, jsii.invoke(self, "putPublicAccessBlockConfiguration", [value]))

    @jsii.member(jsii_name="putVpcConfiguration")
    def put_vpc_configuration(self, *, vpc_id: builtins.str) -> None:
        '''
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#vpc_id S3AccessPoint#vpc_id}.
        '''
        value = S3AccessPointVpcConfiguration(vpc_id=vpc_id)

        return typing.cast(None, jsii.invoke(self, "putVpcConfiguration", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @jsii.member(jsii_name="resetPublicAccessBlockConfiguration")
    def reset_public_access_block_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccessBlockConfiguration", []))

    @jsii.member(jsii_name="resetVpcConfiguration")
    def reset_vpc_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcConfiguration", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasPublicAccessPolicy")
    def has_public_access_policy(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "hasPublicAccessPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkOrigin")
    def network_origin(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkOrigin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccessBlockConfiguration")
    def public_access_block_configuration(
        self,
    ) -> "S3AccessPointPublicAccessBlockConfigurationOutputReference":
        return typing.cast("S3AccessPointPublicAccessBlockConfigurationOutputReference", jsii.get(self, "publicAccessBlockConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConfiguration")
    def vpc_configuration(self) -> "S3AccessPointVpcConfigurationOutputReference":
        return typing.cast("S3AccessPointVpcConfigurationOutputReference", jsii.get(self, "vpcConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccessBlockConfigurationInput")
    def public_access_block_configuration_input(
        self,
    ) -> typing.Optional["S3AccessPointPublicAccessBlockConfiguration"]:
        return typing.cast(typing.Optional["S3AccessPointPublicAccessBlockConfiguration"], jsii.get(self, "publicAccessBlockConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConfigurationInput")
    def vpc_configuration_input(
        self,
    ) -> typing.Optional["S3AccessPointVpcConfiguration"]:
        return typing.cast(typing.Optional["S3AccessPointVpcConfiguration"], jsii.get(self, "vpcConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3AccessPointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "name": "name",
        "account_id": "accountId",
        "policy": "policy",
        "public_access_block_configuration": "publicAccessBlockConfiguration",
        "vpc_configuration": "vpcConfiguration",
    },
)
class S3AccessPointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        public_access_block_configuration: typing.Optional["S3AccessPointPublicAccessBlockConfiguration"] = None,
        vpc_configuration: typing.Optional["S3AccessPointVpcConfiguration"] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#bucket S3AccessPoint#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#name S3AccessPoint#name}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#account_id S3AccessPoint#account_id}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#policy S3AccessPoint#policy}.
        :param public_access_block_configuration: public_access_block_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#public_access_block_configuration S3AccessPoint#public_access_block_configuration}
        :param vpc_configuration: vpc_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#vpc_configuration S3AccessPoint#vpc_configuration}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(public_access_block_configuration, dict):
            public_access_block_configuration = S3AccessPointPublicAccessBlockConfiguration(**public_access_block_configuration)
        if isinstance(vpc_configuration, dict):
            vpc_configuration = S3AccessPointVpcConfiguration(**vpc_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if policy is not None:
            self._values["policy"] = policy
        if public_access_block_configuration is not None:
            self._values["public_access_block_configuration"] = public_access_block_configuration
        if vpc_configuration is not None:
            self._values["vpc_configuration"] = vpc_configuration

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#bucket S3AccessPoint#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#name S3AccessPoint#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#account_id S3AccessPoint#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#policy S3AccessPoint#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_access_block_configuration(
        self,
    ) -> typing.Optional["S3AccessPointPublicAccessBlockConfiguration"]:
        '''public_access_block_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#public_access_block_configuration S3AccessPoint#public_access_block_configuration}
        '''
        result = self._values.get("public_access_block_configuration")
        return typing.cast(typing.Optional["S3AccessPointPublicAccessBlockConfiguration"], result)

    @builtins.property
    def vpc_configuration(self) -> typing.Optional["S3AccessPointVpcConfiguration"]:
        '''vpc_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#vpc_configuration S3AccessPoint#vpc_configuration}
        '''
        result = self._values.get("vpc_configuration")
        return typing.cast(typing.Optional["S3AccessPointVpcConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3AccessPointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3AccessPointPublicAccessBlockConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "block_public_acls": "blockPublicAcls",
        "block_public_policy": "blockPublicPolicy",
        "ignore_public_acls": "ignorePublicAcls",
        "restrict_public_buckets": "restrictPublicBuckets",
    },
)
class S3AccessPointPublicAccessBlockConfiguration:
    def __init__(
        self,
        *,
        block_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restrict_public_buckets: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param block_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#block_public_acls S3AccessPoint#block_public_acls}.
        :param block_public_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#block_public_policy S3AccessPoint#block_public_policy}.
        :param ignore_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#ignore_public_acls S3AccessPoint#ignore_public_acls}.
        :param restrict_public_buckets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#restrict_public_buckets S3AccessPoint#restrict_public_buckets}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if block_public_acls is not None:
            self._values["block_public_acls"] = block_public_acls
        if block_public_policy is not None:
            self._values["block_public_policy"] = block_public_policy
        if ignore_public_acls is not None:
            self._values["ignore_public_acls"] = ignore_public_acls
        if restrict_public_buckets is not None:
            self._values["restrict_public_buckets"] = restrict_public_buckets

    @builtins.property
    def block_public_acls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#block_public_acls S3AccessPoint#block_public_acls}.'''
        result = self._values.get("block_public_acls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def block_public_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#block_public_policy S3AccessPoint#block_public_policy}.'''
        result = self._values.get("block_public_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ignore_public_acls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#ignore_public_acls S3AccessPoint#ignore_public_acls}.'''
        result = self._values.get("ignore_public_acls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def restrict_public_buckets(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#restrict_public_buckets S3AccessPoint#restrict_public_buckets}.'''
        result = self._values.get("restrict_public_buckets")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3AccessPointPublicAccessBlockConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3AccessPointPublicAccessBlockConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3AccessPointPublicAccessBlockConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetBlockPublicAcls")
    def reset_block_public_acls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPublicAcls", []))

    @jsii.member(jsii_name="resetBlockPublicPolicy")
    def reset_block_public_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPublicPolicy", []))

    @jsii.member(jsii_name="resetIgnorePublicAcls")
    def reset_ignore_public_acls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnorePublicAcls", []))

    @jsii.member(jsii_name="resetRestrictPublicBuckets")
    def reset_restrict_public_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictPublicBuckets", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicAclsInput")
    def block_public_acls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "blockPublicAclsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicPolicyInput")
    def block_public_policy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "blockPublicPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePublicAclsInput")
    def ignore_public_acls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ignorePublicAclsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictPublicBucketsInput")
    def restrict_public_buckets_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "restrictPublicBucketsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicAcls")
    def block_public_acls(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "blockPublicAcls"))

    @block_public_acls.setter
    def block_public_acls(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "blockPublicAcls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicPolicy")
    def block_public_policy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "blockPublicPolicy"))

    @block_public_policy.setter
    def block_public_policy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "blockPublicPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePublicAcls")
    def ignore_public_acls(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ignorePublicAcls"))

    @ignore_public_acls.setter
    def ignore_public_acls(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ignorePublicAcls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictPublicBuckets")
    def restrict_public_buckets(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "restrictPublicBuckets"))

    @restrict_public_buckets.setter
    def restrict_public_buckets(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "restrictPublicBuckets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3AccessPointPublicAccessBlockConfiguration]:
        return typing.cast(typing.Optional[S3AccessPointPublicAccessBlockConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3AccessPointPublicAccessBlockConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3AccessPointVpcConfiguration",
    jsii_struct_bases=[],
    name_mapping={"vpc_id": "vpcId"},
)
class S3AccessPointVpcConfiguration:
    def __init__(self, *, vpc_id: builtins.str) -> None:
        '''
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#vpc_id S3AccessPoint#vpc_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "vpc_id": vpc_id,
        }

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_access_point#vpc_id S3AccessPoint#vpc_id}.'''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3AccessPointVpcConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3AccessPointVpcConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3AccessPointVpcConfigurationOutputReference",
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
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3AccessPointVpcConfiguration]:
        return typing.cast(typing.Optional[S3AccessPointVpcConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3AccessPointVpcConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3AccountPublicAccessBlock(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3AccountPublicAccessBlock",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block aws_s3_account_public_access_block}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_id: typing.Optional[builtins.str] = None,
        block_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restrict_public_buckets: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block aws_s3_account_public_access_block} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#account_id S3AccountPublicAccessBlock#account_id}.
        :param block_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#block_public_acls S3AccountPublicAccessBlock#block_public_acls}.
        :param block_public_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#block_public_policy S3AccountPublicAccessBlock#block_public_policy}.
        :param ignore_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#ignore_public_acls S3AccountPublicAccessBlock#ignore_public_acls}.
        :param restrict_public_buckets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#restrict_public_buckets S3AccountPublicAccessBlock#restrict_public_buckets}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3AccountPublicAccessBlockConfig(
            account_id=account_id,
            block_public_acls=block_public_acls,
            block_public_policy=block_public_policy,
            ignore_public_acls=ignore_public_acls,
            restrict_public_buckets=restrict_public_buckets,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetBlockPublicAcls")
    def reset_block_public_acls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPublicAcls", []))

    @jsii.member(jsii_name="resetBlockPublicPolicy")
    def reset_block_public_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPublicPolicy", []))

    @jsii.member(jsii_name="resetIgnorePublicAcls")
    def reset_ignore_public_acls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnorePublicAcls", []))

    @jsii.member(jsii_name="resetRestrictPublicBuckets")
    def reset_restrict_public_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictPublicBuckets", []))

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
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicAclsInput")
    def block_public_acls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "blockPublicAclsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicPolicyInput")
    def block_public_policy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "blockPublicPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePublicAclsInput")
    def ignore_public_acls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ignorePublicAclsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictPublicBucketsInput")
    def restrict_public_buckets_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "restrictPublicBucketsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicAcls")
    def block_public_acls(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "blockPublicAcls"))

    @block_public_acls.setter
    def block_public_acls(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "blockPublicAcls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicPolicy")
    def block_public_policy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "blockPublicPolicy"))

    @block_public_policy.setter
    def block_public_policy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "blockPublicPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePublicAcls")
    def ignore_public_acls(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ignorePublicAcls"))

    @ignore_public_acls.setter
    def ignore_public_acls(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ignorePublicAcls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictPublicBuckets")
    def restrict_public_buckets(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "restrictPublicBuckets"))

    @restrict_public_buckets.setter
    def restrict_public_buckets(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "restrictPublicBuckets", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3AccountPublicAccessBlockConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "account_id": "accountId",
        "block_public_acls": "blockPublicAcls",
        "block_public_policy": "blockPublicPolicy",
        "ignore_public_acls": "ignorePublicAcls",
        "restrict_public_buckets": "restrictPublicBuckets",
    },
)
class S3AccountPublicAccessBlockConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        account_id: typing.Optional[builtins.str] = None,
        block_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restrict_public_buckets: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#account_id S3AccountPublicAccessBlock#account_id}.
        :param block_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#block_public_acls S3AccountPublicAccessBlock#block_public_acls}.
        :param block_public_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#block_public_policy S3AccountPublicAccessBlock#block_public_policy}.
        :param ignore_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#ignore_public_acls S3AccountPublicAccessBlock#ignore_public_acls}.
        :param restrict_public_buckets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#restrict_public_buckets S3AccountPublicAccessBlock#restrict_public_buckets}.
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
        if account_id is not None:
            self._values["account_id"] = account_id
        if block_public_acls is not None:
            self._values["block_public_acls"] = block_public_acls
        if block_public_policy is not None:
            self._values["block_public_policy"] = block_public_policy
        if ignore_public_acls is not None:
            self._values["ignore_public_acls"] = ignore_public_acls
        if restrict_public_buckets is not None:
            self._values["restrict_public_buckets"] = restrict_public_buckets

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
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#account_id S3AccountPublicAccessBlock#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_public_acls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#block_public_acls S3AccountPublicAccessBlock#block_public_acls}.'''
        result = self._values.get("block_public_acls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def block_public_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#block_public_policy S3AccountPublicAccessBlock#block_public_policy}.'''
        result = self._values.get("block_public_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ignore_public_acls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#ignore_public_acls S3AccountPublicAccessBlock#ignore_public_acls}.'''
        result = self._values.get("ignore_public_acls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def restrict_public_buckets(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_account_public_access_block#restrict_public_buckets S3AccountPublicAccessBlock#restrict_public_buckets}.'''
        result = self._values.get("restrict_public_buckets")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3AccountPublicAccessBlockConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3Bucket(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3Bucket",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket aws_s3_bucket}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        acceleration_status: typing.Optional[builtins.str] = None,
        acl: typing.Optional[builtins.str] = None,
        bucket: typing.Optional[builtins.str] = None,
        bucket_prefix: typing.Optional[builtins.str] = None,
        cors_rule: typing.Optional[typing.Sequence["S3BucketCorsRule"]] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        grant: typing.Optional[typing.Sequence["S3BucketGrant"]] = None,
        hosted_zone_id: typing.Optional[builtins.str] = None,
        lifecycle_rule: typing.Optional[typing.Sequence["S3BucketLifecycleRule"]] = None,
        logging: typing.Optional[typing.Sequence["S3BucketLogging"]] = None,
        object_lock_configuration: typing.Optional["S3BucketObjectLockConfiguration"] = None,
        policy: typing.Optional[builtins.str] = None,
        replication_configuration: typing.Optional["S3BucketReplicationConfiguration"] = None,
        request_payer: typing.Optional[builtins.str] = None,
        server_side_encryption_configuration: typing.Optional["S3BucketServerSideEncryptionConfiguration"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        versioning: typing.Optional["S3BucketVersioning"] = None,
        website: typing.Optional["S3BucketWebsite"] = None,
        website_domain: typing.Optional[builtins.str] = None,
        website_endpoint: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket aws_s3_bucket} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param acceleration_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#acceleration_status S3Bucket#acceleration_status}.
        :param acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#acl S3Bucket#acl}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket S3Bucket#bucket}.
        :param bucket_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket_prefix S3Bucket#bucket_prefix}.
        :param cors_rule: cors_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#cors_rule S3Bucket#cors_rule}
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#force_destroy S3Bucket#force_destroy}.
        :param grant: grant block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#grant S3Bucket#grant}
        :param hosted_zone_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#hosted_zone_id S3Bucket#hosted_zone_id}.
        :param lifecycle_rule: lifecycle_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#lifecycle_rule S3Bucket#lifecycle_rule}
        :param logging: logging block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#logging S3Bucket#logging}
        :param object_lock_configuration: object_lock_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#object_lock_configuration S3Bucket#object_lock_configuration}
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#policy S3Bucket#policy}.
        :param replication_configuration: replication_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#replication_configuration S3Bucket#replication_configuration}
        :param request_payer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#request_payer S3Bucket#request_payer}.
        :param server_side_encryption_configuration: server_side_encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#server_side_encryption_configuration S3Bucket#server_side_encryption_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags S3Bucket#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags_all S3Bucket#tags_all}.
        :param versioning: versioning block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#versioning S3Bucket#versioning}
        :param website: website block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#website S3Bucket#website}
        :param website_domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#website_domain S3Bucket#website_domain}.
        :param website_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#website_endpoint S3Bucket#website_endpoint}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketConfig(
            acceleration_status=acceleration_status,
            acl=acl,
            bucket=bucket,
            bucket_prefix=bucket_prefix,
            cors_rule=cors_rule,
            force_destroy=force_destroy,
            grant=grant,
            hosted_zone_id=hosted_zone_id,
            lifecycle_rule=lifecycle_rule,
            logging=logging,
            object_lock_configuration=object_lock_configuration,
            policy=policy,
            replication_configuration=replication_configuration,
            request_payer=request_payer,
            server_side_encryption_configuration=server_side_encryption_configuration,
            tags=tags,
            tags_all=tags_all,
            versioning=versioning,
            website=website,
            website_domain=website_domain,
            website_endpoint=website_endpoint,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putObjectLockConfiguration")
    def put_object_lock_configuration(
        self,
        *,
        object_lock_enabled: builtins.str,
        rule: typing.Optional["S3BucketObjectLockConfigurationRule"] = None,
    ) -> None:
        '''
        :param object_lock_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#object_lock_enabled S3Bucket#object_lock_enabled}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#rule S3Bucket#rule}
        '''
        value = S3BucketObjectLockConfiguration(
            object_lock_enabled=object_lock_enabled, rule=rule
        )

        return typing.cast(None, jsii.invoke(self, "putObjectLockConfiguration", [value]))

    @jsii.member(jsii_name="putReplicationConfiguration")
    def put_replication_configuration(
        self,
        *,
        role: builtins.str,
        rules: typing.Sequence["S3BucketReplicationConfigurationRules"],
    ) -> None:
        '''
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#role S3Bucket#role}.
        :param rules: rules block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#rules S3Bucket#rules}
        '''
        value = S3BucketReplicationConfiguration(role=role, rules=rules)

        return typing.cast(None, jsii.invoke(self, "putReplicationConfiguration", [value]))

    @jsii.member(jsii_name="putServerSideEncryptionConfiguration")
    def put_server_side_encryption_configuration(
        self,
        *,
        rule: "S3BucketServerSideEncryptionConfigurationRule",
    ) -> None:
        '''
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#rule S3Bucket#rule}
        '''
        value = S3BucketServerSideEncryptionConfiguration(rule=rule)

        return typing.cast(None, jsii.invoke(self, "putServerSideEncryptionConfiguration", [value]))

    @jsii.member(jsii_name="putVersioning")
    def put_versioning(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        mfa_delete: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#enabled S3Bucket#enabled}.
        :param mfa_delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#mfa_delete S3Bucket#mfa_delete}.
        '''
        value = S3BucketVersioning(enabled=enabled, mfa_delete=mfa_delete)

        return typing.cast(None, jsii.invoke(self, "putVersioning", [value]))

    @jsii.member(jsii_name="putWebsite")
    def put_website(
        self,
        *,
        error_document: typing.Optional[builtins.str] = None,
        index_document: typing.Optional[builtins.str] = None,
        redirect_all_requests_to: typing.Optional[builtins.str] = None,
        routing_rules: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param error_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#error_document S3Bucket#error_document}.
        :param index_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#index_document S3Bucket#index_document}.
        :param redirect_all_requests_to: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#redirect_all_requests_to S3Bucket#redirect_all_requests_to}.
        :param routing_rules: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#routing_rules S3Bucket#routing_rules}.
        '''
        value = S3BucketWebsite(
            error_document=error_document,
            index_document=index_document,
            redirect_all_requests_to=redirect_all_requests_to,
            routing_rules=routing_rules,
        )

        return typing.cast(None, jsii.invoke(self, "putWebsite", [value]))

    @jsii.member(jsii_name="resetAccelerationStatus")
    def reset_acceleration_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccelerationStatus", []))

    @jsii.member(jsii_name="resetAcl")
    def reset_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAcl", []))

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetBucketPrefix")
    def reset_bucket_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketPrefix", []))

    @jsii.member(jsii_name="resetCorsRule")
    def reset_cors_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCorsRule", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetGrant")
    def reset_grant(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGrant", []))

    @jsii.member(jsii_name="resetHostedZoneId")
    def reset_hosted_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostedZoneId", []))

    @jsii.member(jsii_name="resetLifecycleRule")
    def reset_lifecycle_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLifecycleRule", []))

    @jsii.member(jsii_name="resetLogging")
    def reset_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogging", []))

    @jsii.member(jsii_name="resetObjectLockConfiguration")
    def reset_object_lock_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockConfiguration", []))

    @jsii.member(jsii_name="resetPolicy")
    def reset_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicy", []))

    @jsii.member(jsii_name="resetReplicationConfiguration")
    def reset_replication_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationConfiguration", []))

    @jsii.member(jsii_name="resetRequestPayer")
    def reset_request_payer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestPayer", []))

    @jsii.member(jsii_name="resetServerSideEncryptionConfiguration")
    def reset_server_side_encryption_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryptionConfiguration", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetVersioning")
    def reset_versioning(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersioning", []))

    @jsii.member(jsii_name="resetWebsite")
    def reset_website(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebsite", []))

    @jsii.member(jsii_name="resetWebsiteDomain")
    def reset_website_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebsiteDomain", []))

    @jsii.member(jsii_name="resetWebsiteEndpoint")
    def reset_website_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebsiteEndpoint", []))

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
    @jsii.member(jsii_name="bucketDomainName")
    def bucket_domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketRegionalDomainName")
    def bucket_regional_domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketRegionalDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockConfiguration")
    def object_lock_configuration(
        self,
    ) -> "S3BucketObjectLockConfigurationOutputReference":
        return typing.cast("S3BucketObjectLockConfigurationOutputReference", jsii.get(self, "objectLockConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationConfiguration")
    def replication_configuration(
        self,
    ) -> "S3BucketReplicationConfigurationOutputReference":
        return typing.cast("S3BucketReplicationConfigurationOutputReference", jsii.get(self, "replicationConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryptionConfiguration")
    def server_side_encryption_configuration(
        self,
    ) -> "S3BucketServerSideEncryptionConfigurationOutputReference":
        return typing.cast("S3BucketServerSideEncryptionConfigurationOutputReference", jsii.get(self, "serverSideEncryptionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versioning")
    def versioning(self) -> "S3BucketVersioningOutputReference":
        return typing.cast("S3BucketVersioningOutputReference", jsii.get(self, "versioning"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="website")
    def website(self) -> "S3BucketWebsiteOutputReference":
        return typing.cast("S3BucketWebsiteOutputReference", jsii.get(self, "website"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accelerationStatusInput")
    def acceleration_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accelerationStatusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclInput")
    def acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aclInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketPrefixInput")
    def bucket_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketPrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="corsRuleInput")
    def cors_rule_input(self) -> typing.Optional[typing.List["S3BucketCorsRule"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketCorsRule"]], jsii.get(self, "corsRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantInput")
    def grant_input(self) -> typing.Optional[typing.List["S3BucketGrant"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketGrant"]], jsii.get(self, "grantInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneIdInput")
    def hosted_zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostedZoneIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lifecycleRuleInput")
    def lifecycle_rule_input(
        self,
    ) -> typing.Optional[typing.List["S3BucketLifecycleRule"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketLifecycleRule"]], jsii.get(self, "lifecycleRuleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingInput")
    def logging_input(self) -> typing.Optional[typing.List["S3BucketLogging"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketLogging"]], jsii.get(self, "loggingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockConfigurationInput")
    def object_lock_configuration_input(
        self,
    ) -> typing.Optional["S3BucketObjectLockConfiguration"]:
        return typing.cast(typing.Optional["S3BucketObjectLockConfiguration"], jsii.get(self, "objectLockConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationConfigurationInput")
    def replication_configuration_input(
        self,
    ) -> typing.Optional["S3BucketReplicationConfiguration"]:
        return typing.cast(typing.Optional["S3BucketReplicationConfiguration"], jsii.get(self, "replicationConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestPayerInput")
    def request_payer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestPayerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryptionConfigurationInput")
    def server_side_encryption_configuration_input(
        self,
    ) -> typing.Optional["S3BucketServerSideEncryptionConfiguration"]:
        return typing.cast(typing.Optional["S3BucketServerSideEncryptionConfiguration"], jsii.get(self, "serverSideEncryptionConfigurationInput"))

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
    @jsii.member(jsii_name="versioningInput")
    def versioning_input(self) -> typing.Optional["S3BucketVersioning"]:
        return typing.cast(typing.Optional["S3BucketVersioning"], jsii.get(self, "versioningInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="websiteDomainInput")
    def website_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "websiteDomainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="websiteEndpointInput")
    def website_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "websiteEndpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="websiteInput")
    def website_input(self) -> typing.Optional["S3BucketWebsite"]:
        return typing.cast(typing.Optional["S3BucketWebsite"], jsii.get(self, "websiteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accelerationStatus")
    def acceleration_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accelerationStatus"))

    @acceleration_status.setter
    def acceleration_status(self, value: builtins.str) -> None:
        jsii.set(self, "accelerationStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acl")
    def acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acl"))

    @acl.setter
    def acl(self, value: builtins.str) -> None:
        jsii.set(self, "acl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketPrefix")
    def bucket_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketPrefix"))

    @bucket_prefix.setter
    def bucket_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "bucketPrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="corsRule")
    def cors_rule(self) -> typing.List["S3BucketCorsRule"]:
        return typing.cast(typing.List["S3BucketCorsRule"], jsii.get(self, "corsRule"))

    @cors_rule.setter
    def cors_rule(self, value: typing.List["S3BucketCorsRule"]) -> None:
        jsii.set(self, "corsRule", value)

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
    @jsii.member(jsii_name="grant")
    def grant(self) -> typing.List["S3BucketGrant"]:
        return typing.cast(typing.List["S3BucketGrant"], jsii.get(self, "grant"))

    @grant.setter
    def grant(self, value: typing.List["S3BucketGrant"]) -> None:
        jsii.set(self, "grant", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @hosted_zone_id.setter
    def hosted_zone_id(self, value: builtins.str) -> None:
        jsii.set(self, "hostedZoneId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lifecycleRule")
    def lifecycle_rule(self) -> typing.List["S3BucketLifecycleRule"]:
        return typing.cast(typing.List["S3BucketLifecycleRule"], jsii.get(self, "lifecycleRule"))

    @lifecycle_rule.setter
    def lifecycle_rule(self, value: typing.List["S3BucketLifecycleRule"]) -> None:
        jsii.set(self, "lifecycleRule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logging")
    def logging(self) -> typing.List["S3BucketLogging"]:
        return typing.cast(typing.List["S3BucketLogging"], jsii.get(self, "logging"))

    @logging.setter
    def logging(self, value: typing.List["S3BucketLogging"]) -> None:
        jsii.set(self, "logging", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestPayer")
    def request_payer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestPayer"))

    @request_payer.setter
    def request_payer(self, value: builtins.str) -> None:
        jsii.set(self, "requestPayer", value)

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
    @jsii.member(jsii_name="websiteDomain")
    def website_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "websiteDomain"))

    @website_domain.setter
    def website_domain(self, value: builtins.str) -> None:
        jsii.set(self, "websiteDomain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="websiteEndpoint")
    def website_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "websiteEndpoint"))

    @website_endpoint.setter
    def website_endpoint(self, value: builtins.str) -> None:
        jsii.set(self, "websiteEndpoint", value)


class S3BucketAnalyticsConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration aws_s3_bucket_analytics_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        name: builtins.str,
        filter: typing.Optional["S3BucketAnalyticsConfigurationFilter"] = None,
        storage_class_analysis: typing.Optional["S3BucketAnalyticsConfigurationStorageClassAnalysis"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration aws_s3_bucket_analytics_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#bucket S3BucketAnalyticsConfiguration#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#name S3BucketAnalyticsConfiguration#name}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#filter S3BucketAnalyticsConfiguration#filter}
        :param storage_class_analysis: storage_class_analysis block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#storage_class_analysis S3BucketAnalyticsConfiguration#storage_class_analysis}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketAnalyticsConfigurationConfig(
            bucket=bucket,
            name=name,
            filter=filter,
            storage_class_analysis=storage_class_analysis,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#prefix S3BucketAnalyticsConfiguration#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#tags S3BucketAnalyticsConfiguration#tags}.
        '''
        value = S3BucketAnalyticsConfigurationFilter(prefix=prefix, tags=tags)

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="putStorageClassAnalysis")
    def put_storage_class_analysis(
        self,
        *,
        data_export: "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport",
    ) -> None:
        '''
        :param data_export: data_export block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#data_export S3BucketAnalyticsConfiguration#data_export}
        '''
        value = S3BucketAnalyticsConfigurationStorageClassAnalysis(
            data_export=data_export
        )

        return typing.cast(None, jsii.invoke(self, "putStorageClassAnalysis", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetStorageClassAnalysis")
    def reset_storage_class_analysis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageClassAnalysis", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "S3BucketAnalyticsConfigurationFilterOutputReference":
        return typing.cast("S3BucketAnalyticsConfigurationFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClassAnalysis")
    def storage_class_analysis(
        self,
    ) -> "S3BucketAnalyticsConfigurationStorageClassAnalysisOutputReference":
        return typing.cast("S3BucketAnalyticsConfigurationStorageClassAnalysisOutputReference", jsii.get(self, "storageClassAnalysis"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(self) -> typing.Optional["S3BucketAnalyticsConfigurationFilter"]:
        return typing.cast(typing.Optional["S3BucketAnalyticsConfigurationFilter"], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClassAnalysisInput")
    def storage_class_analysis_input(
        self,
    ) -> typing.Optional["S3BucketAnalyticsConfigurationStorageClassAnalysis"]:
        return typing.cast(typing.Optional["S3BucketAnalyticsConfigurationStorageClassAnalysis"], jsii.get(self, "storageClassAnalysisInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "name": "name",
        "filter": "filter",
        "storage_class_analysis": "storageClassAnalysis",
    },
)
class S3BucketAnalyticsConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        name: builtins.str,
        filter: typing.Optional["S3BucketAnalyticsConfigurationFilter"] = None,
        storage_class_analysis: typing.Optional["S3BucketAnalyticsConfigurationStorageClassAnalysis"] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#bucket S3BucketAnalyticsConfiguration#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#name S3BucketAnalyticsConfiguration#name}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#filter S3BucketAnalyticsConfiguration#filter}
        :param storage_class_analysis: storage_class_analysis block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#storage_class_analysis S3BucketAnalyticsConfiguration#storage_class_analysis}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = S3BucketAnalyticsConfigurationFilter(**filter)
        if isinstance(storage_class_analysis, dict):
            storage_class_analysis = S3BucketAnalyticsConfigurationStorageClassAnalysis(**storage_class_analysis)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
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
        if filter is not None:
            self._values["filter"] = filter
        if storage_class_analysis is not None:
            self._values["storage_class_analysis"] = storage_class_analysis

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#bucket S3BucketAnalyticsConfiguration#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#name S3BucketAnalyticsConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(self) -> typing.Optional["S3BucketAnalyticsConfigurationFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#filter S3BucketAnalyticsConfiguration#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["S3BucketAnalyticsConfigurationFilter"], result)

    @builtins.property
    def storage_class_analysis(
        self,
    ) -> typing.Optional["S3BucketAnalyticsConfigurationStorageClassAnalysis"]:
        '''storage_class_analysis block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#storage_class_analysis S3BucketAnalyticsConfiguration#storage_class_analysis}
        '''
        result = self._values.get("storage_class_analysis")
        return typing.cast(typing.Optional["S3BucketAnalyticsConfigurationStorageClassAnalysis"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketAnalyticsConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationFilter",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix", "tags": "tags"},
)
class S3BucketAnalyticsConfigurationFilter:
    def __init__(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#prefix S3BucketAnalyticsConfiguration#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#tags S3BucketAnalyticsConfiguration#tags}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#prefix S3BucketAnalyticsConfiguration#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#tags S3BucketAnalyticsConfiguration#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketAnalyticsConfigurationFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketAnalyticsConfigurationFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationFilterOutputReference",
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

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketAnalyticsConfigurationFilter]:
        return typing.cast(typing.Optional[S3BucketAnalyticsConfigurationFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketAnalyticsConfigurationFilter],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationStorageClassAnalysis",
    jsii_struct_bases=[],
    name_mapping={"data_export": "dataExport"},
)
class S3BucketAnalyticsConfigurationStorageClassAnalysis:
    def __init__(
        self,
        *,
        data_export: "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport",
    ) -> None:
        '''
        :param data_export: data_export block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#data_export S3BucketAnalyticsConfiguration#data_export}
        '''
        if isinstance(data_export, dict):
            data_export = S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport(**data_export)
        self._values: typing.Dict[str, typing.Any] = {
            "data_export": data_export,
        }

    @builtins.property
    def data_export(
        self,
    ) -> "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport":
        '''data_export block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#data_export S3BucketAnalyticsConfiguration#data_export}
        '''
        result = self._values.get("data_export")
        assert result is not None, "Required property 'data_export' is missing"
        return typing.cast("S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketAnalyticsConfigurationStorageClassAnalysis(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "output_schema_version": "outputSchemaVersion",
    },
)
class S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport:
    def __init__(
        self,
        *,
        destination: "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination",
        output_schema_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#destination S3BucketAnalyticsConfiguration#destination}
        :param output_schema_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#output_schema_version S3BucketAnalyticsConfiguration#output_schema_version}.
        '''
        if isinstance(destination, dict):
            destination = S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination(**destination)
        self._values: typing.Dict[str, typing.Any] = {
            "destination": destination,
        }
        if output_schema_version is not None:
            self._values["output_schema_version"] = output_schema_version

    @builtins.property
    def destination(
        self,
    ) -> "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination":
        '''destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#destination S3BucketAnalyticsConfiguration#destination}
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination", result)

    @builtins.property
    def output_schema_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#output_schema_version S3BucketAnalyticsConfiguration#output_schema_version}.'''
        result = self._values.get("output_schema_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination",
    jsii_struct_bases=[],
    name_mapping={"s3_bucket_destination": "s3BucketDestination"},
)
class S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination:
    def __init__(
        self,
        *,
        s3_bucket_destination: "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination",
    ) -> None:
        '''
        :param s3_bucket_destination: s3_bucket_destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#s3_bucket_destination S3BucketAnalyticsConfiguration#s3_bucket_destination}
        '''
        if isinstance(s3_bucket_destination, dict):
            s3_bucket_destination = S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination(**s3_bucket_destination)
        self._values: typing.Dict[str, typing.Any] = {
            "s3_bucket_destination": s3_bucket_destination,
        }

    @builtins.property
    def s3_bucket_destination(
        self,
    ) -> "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination":
        '''s3_bucket_destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#s3_bucket_destination S3BucketAnalyticsConfiguration#s3_bucket_destination}
        '''
        result = self._values.get("s3_bucket_destination")
        assert result is not None, "Required property 's3_bucket_destination' is missing"
        return typing.cast("S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationOutputReference",
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

    @jsii.member(jsii_name="putS3BucketDestination")
    def put_s3_bucket_destination(
        self,
        *,
        bucket_arn: builtins.str,
        bucket_account_id: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#bucket_arn S3BucketAnalyticsConfiguration#bucket_arn}.
        :param bucket_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#bucket_account_id S3BucketAnalyticsConfiguration#bucket_account_id}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#format S3BucketAnalyticsConfiguration#format}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#prefix S3BucketAnalyticsConfiguration#prefix}.
        '''
        value = S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination(
            bucket_arn=bucket_arn,
            bucket_account_id=bucket_account_id,
            format=format,
            prefix=prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putS3BucketDestination", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketDestination")
    def s3_bucket_destination(
        self,
    ) -> "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestinationOutputReference":
        return typing.cast("S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestinationOutputReference", jsii.get(self, "s3BucketDestination"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketDestinationInput")
    def s3_bucket_destination_input(
        self,
    ) -> typing.Optional["S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination"]:
        return typing.cast(typing.Optional["S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination"], jsii.get(self, "s3BucketDestinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination]:
        return typing.cast(typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_arn": "bucketArn",
        "bucket_account_id": "bucketAccountId",
        "format": "format",
        "prefix": "prefix",
    },
)
class S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination:
    def __init__(
        self,
        *,
        bucket_arn: builtins.str,
        bucket_account_id: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#bucket_arn S3BucketAnalyticsConfiguration#bucket_arn}.
        :param bucket_account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#bucket_account_id S3BucketAnalyticsConfiguration#bucket_account_id}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#format S3BucketAnalyticsConfiguration#format}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#prefix S3BucketAnalyticsConfiguration#prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_arn": bucket_arn,
        }
        if bucket_account_id is not None:
            self._values["bucket_account_id"] = bucket_account_id
        if format is not None:
            self._values["format"] = format
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def bucket_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#bucket_arn S3BucketAnalyticsConfiguration#bucket_arn}.'''
        result = self._values.get("bucket_arn")
        assert result is not None, "Required property 'bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#bucket_account_id S3BucketAnalyticsConfiguration#bucket_account_id}.'''
        result = self._values.get("bucket_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#format S3BucketAnalyticsConfiguration#format}.'''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#prefix S3BucketAnalyticsConfiguration#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestinationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestinationOutputReference",
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

    @jsii.member(jsii_name="resetBucketAccountId")
    def reset_bucket_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketAccountId", []))

    @jsii.member(jsii_name="resetFormat")
    def reset_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFormat", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAccountIdInput")
    def bucket_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketArnInput")
    def bucket_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAccountId")
    def bucket_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketAccountId"))

    @bucket_account_id.setter
    def bucket_account_id(self, value: builtins.str) -> None:
        jsii.set(self, "bucketAccountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketArn")
    def bucket_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketArn"))

    @bucket_arn.setter
    def bucket_arn(self, value: builtins.str) -> None:
        jsii.set(self, "bucketArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        jsii.set(self, "format", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination]:
        return typing.cast(typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportOutputReference",
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

    @jsii.member(jsii_name="putDestination")
    def put_destination(
        self,
        *,
        s3_bucket_destination: S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination,
    ) -> None:
        '''
        :param s3_bucket_destination: s3_bucket_destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#s3_bucket_destination S3BucketAnalyticsConfiguration#s3_bucket_destination}
        '''
        value = S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination(
            s3_bucket_destination=s3_bucket_destination
        )

        return typing.cast(None, jsii.invoke(self, "putDestination", [value]))

    @jsii.member(jsii_name="resetOutputSchemaVersion")
    def reset_output_schema_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputSchemaVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destination")
    def destination(
        self,
    ) -> S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationOutputReference:
        return typing.cast(S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationOutputReference, jsii.get(self, "destination"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationInput")
    def destination_input(
        self,
    ) -> typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination]:
        return typing.cast(typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination], jsii.get(self, "destinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSchemaVersionInput")
    def output_schema_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputSchemaVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSchemaVersion")
    def output_schema_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputSchemaVersion"))

    @output_schema_version.setter
    def output_schema_version(self, value: builtins.str) -> None:
        jsii.set(self, "outputSchemaVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport]:
        return typing.cast(typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketAnalyticsConfigurationStorageClassAnalysisOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketAnalyticsConfigurationStorageClassAnalysisOutputReference",
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

    @jsii.member(jsii_name="putDataExport")
    def put_data_export(
        self,
        *,
        destination: S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination,
        output_schema_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#destination S3BucketAnalyticsConfiguration#destination}
        :param output_schema_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_analytics_configuration#output_schema_version S3BucketAnalyticsConfiguration#output_schema_version}.
        '''
        value = S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport(
            destination=destination, output_schema_version=output_schema_version
        )

        return typing.cast(None, jsii.invoke(self, "putDataExport", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataExport")
    def data_export(
        self,
    ) -> S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportOutputReference:
        return typing.cast(S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportOutputReference, jsii.get(self, "dataExport"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataExportInput")
    def data_export_input(
        self,
    ) -> typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport]:
        return typing.cast(typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport], jsii.get(self, "dataExportInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysis]:
        return typing.cast(typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysis], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketAnalyticsConfigurationStorageClassAnalysis],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "acceleration_status": "accelerationStatus",
        "acl": "acl",
        "bucket": "bucket",
        "bucket_prefix": "bucketPrefix",
        "cors_rule": "corsRule",
        "force_destroy": "forceDestroy",
        "grant": "grant",
        "hosted_zone_id": "hostedZoneId",
        "lifecycle_rule": "lifecycleRule",
        "logging": "logging",
        "object_lock_configuration": "objectLockConfiguration",
        "policy": "policy",
        "replication_configuration": "replicationConfiguration",
        "request_payer": "requestPayer",
        "server_side_encryption_configuration": "serverSideEncryptionConfiguration",
        "tags": "tags",
        "tags_all": "tagsAll",
        "versioning": "versioning",
        "website": "website",
        "website_domain": "websiteDomain",
        "website_endpoint": "websiteEndpoint",
    },
)
class S3BucketConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        acceleration_status: typing.Optional[builtins.str] = None,
        acl: typing.Optional[builtins.str] = None,
        bucket: typing.Optional[builtins.str] = None,
        bucket_prefix: typing.Optional[builtins.str] = None,
        cors_rule: typing.Optional[typing.Sequence["S3BucketCorsRule"]] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        grant: typing.Optional[typing.Sequence["S3BucketGrant"]] = None,
        hosted_zone_id: typing.Optional[builtins.str] = None,
        lifecycle_rule: typing.Optional[typing.Sequence["S3BucketLifecycleRule"]] = None,
        logging: typing.Optional[typing.Sequence["S3BucketLogging"]] = None,
        object_lock_configuration: typing.Optional["S3BucketObjectLockConfiguration"] = None,
        policy: typing.Optional[builtins.str] = None,
        replication_configuration: typing.Optional["S3BucketReplicationConfiguration"] = None,
        request_payer: typing.Optional[builtins.str] = None,
        server_side_encryption_configuration: typing.Optional["S3BucketServerSideEncryptionConfiguration"] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        versioning: typing.Optional["S3BucketVersioning"] = None,
        website: typing.Optional["S3BucketWebsite"] = None,
        website_domain: typing.Optional[builtins.str] = None,
        website_endpoint: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param acceleration_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#acceleration_status S3Bucket#acceleration_status}.
        :param acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#acl S3Bucket#acl}.
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket S3Bucket#bucket}.
        :param bucket_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket_prefix S3Bucket#bucket_prefix}.
        :param cors_rule: cors_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#cors_rule S3Bucket#cors_rule}
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#force_destroy S3Bucket#force_destroy}.
        :param grant: grant block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#grant S3Bucket#grant}
        :param hosted_zone_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#hosted_zone_id S3Bucket#hosted_zone_id}.
        :param lifecycle_rule: lifecycle_rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#lifecycle_rule S3Bucket#lifecycle_rule}
        :param logging: logging block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#logging S3Bucket#logging}
        :param object_lock_configuration: object_lock_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#object_lock_configuration S3Bucket#object_lock_configuration}
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#policy S3Bucket#policy}.
        :param replication_configuration: replication_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#replication_configuration S3Bucket#replication_configuration}
        :param request_payer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#request_payer S3Bucket#request_payer}.
        :param server_side_encryption_configuration: server_side_encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#server_side_encryption_configuration S3Bucket#server_side_encryption_configuration}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags S3Bucket#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags_all S3Bucket#tags_all}.
        :param versioning: versioning block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#versioning S3Bucket#versioning}
        :param website: website block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#website S3Bucket#website}
        :param website_domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#website_domain S3Bucket#website_domain}.
        :param website_endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#website_endpoint S3Bucket#website_endpoint}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(object_lock_configuration, dict):
            object_lock_configuration = S3BucketObjectLockConfiguration(**object_lock_configuration)
        if isinstance(replication_configuration, dict):
            replication_configuration = S3BucketReplicationConfiguration(**replication_configuration)
        if isinstance(server_side_encryption_configuration, dict):
            server_side_encryption_configuration = S3BucketServerSideEncryptionConfiguration(**server_side_encryption_configuration)
        if isinstance(versioning, dict):
            versioning = S3BucketVersioning(**versioning)
        if isinstance(website, dict):
            website = S3BucketWebsite(**website)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if acceleration_status is not None:
            self._values["acceleration_status"] = acceleration_status
        if acl is not None:
            self._values["acl"] = acl
        if bucket is not None:
            self._values["bucket"] = bucket
        if bucket_prefix is not None:
            self._values["bucket_prefix"] = bucket_prefix
        if cors_rule is not None:
            self._values["cors_rule"] = cors_rule
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if grant is not None:
            self._values["grant"] = grant
        if hosted_zone_id is not None:
            self._values["hosted_zone_id"] = hosted_zone_id
        if lifecycle_rule is not None:
            self._values["lifecycle_rule"] = lifecycle_rule
        if logging is not None:
            self._values["logging"] = logging
        if object_lock_configuration is not None:
            self._values["object_lock_configuration"] = object_lock_configuration
        if policy is not None:
            self._values["policy"] = policy
        if replication_configuration is not None:
            self._values["replication_configuration"] = replication_configuration
        if request_payer is not None:
            self._values["request_payer"] = request_payer
        if server_side_encryption_configuration is not None:
            self._values["server_side_encryption_configuration"] = server_side_encryption_configuration
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if versioning is not None:
            self._values["versioning"] = versioning
        if website is not None:
            self._values["website"] = website
        if website_domain is not None:
            self._values["website_domain"] = website_domain
        if website_endpoint is not None:
            self._values["website_endpoint"] = website_endpoint

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
    def acceleration_status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#acceleration_status S3Bucket#acceleration_status}.'''
        result = self._values.get("acceleration_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#acl S3Bucket#acl}.'''
        result = self._values.get("acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket S3Bucket#bucket}.'''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket_prefix S3Bucket#bucket_prefix}.'''
        result = self._values.get("bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cors_rule(self) -> typing.Optional[typing.List["S3BucketCorsRule"]]:
        '''cors_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#cors_rule S3Bucket#cors_rule}
        '''
        result = self._values.get("cors_rule")
        return typing.cast(typing.Optional[typing.List["S3BucketCorsRule"]], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#force_destroy S3Bucket#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def grant(self) -> typing.Optional[typing.List["S3BucketGrant"]]:
        '''grant block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#grant S3Bucket#grant}
        '''
        result = self._values.get("grant")
        return typing.cast(typing.Optional[typing.List["S3BucketGrant"]], result)

    @builtins.property
    def hosted_zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#hosted_zone_id S3Bucket#hosted_zone_id}.'''
        result = self._values.get("hosted_zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lifecycle_rule(self) -> typing.Optional[typing.List["S3BucketLifecycleRule"]]:
        '''lifecycle_rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#lifecycle_rule S3Bucket#lifecycle_rule}
        '''
        result = self._values.get("lifecycle_rule")
        return typing.cast(typing.Optional[typing.List["S3BucketLifecycleRule"]], result)

    @builtins.property
    def logging(self) -> typing.Optional[typing.List["S3BucketLogging"]]:
        '''logging block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#logging S3Bucket#logging}
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[typing.List["S3BucketLogging"]], result)

    @builtins.property
    def object_lock_configuration(
        self,
    ) -> typing.Optional["S3BucketObjectLockConfiguration"]:
        '''object_lock_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#object_lock_configuration S3Bucket#object_lock_configuration}
        '''
        result = self._values.get("object_lock_configuration")
        return typing.cast(typing.Optional["S3BucketObjectLockConfiguration"], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#policy S3Bucket#policy}.'''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_configuration(
        self,
    ) -> typing.Optional["S3BucketReplicationConfiguration"]:
        '''replication_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#replication_configuration S3Bucket#replication_configuration}
        '''
        result = self._values.get("replication_configuration")
        return typing.cast(typing.Optional["S3BucketReplicationConfiguration"], result)

    @builtins.property
    def request_payer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#request_payer S3Bucket#request_payer}.'''
        result = self._values.get("request_payer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_encryption_configuration(
        self,
    ) -> typing.Optional["S3BucketServerSideEncryptionConfiguration"]:
        '''server_side_encryption_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#server_side_encryption_configuration S3Bucket#server_side_encryption_configuration}
        '''
        result = self._values.get("server_side_encryption_configuration")
        return typing.cast(typing.Optional["S3BucketServerSideEncryptionConfiguration"], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags S3Bucket#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags_all S3Bucket#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def versioning(self) -> typing.Optional["S3BucketVersioning"]:
        '''versioning block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#versioning S3Bucket#versioning}
        '''
        result = self._values.get("versioning")
        return typing.cast(typing.Optional["S3BucketVersioning"], result)

    @builtins.property
    def website(self) -> typing.Optional["S3BucketWebsite"]:
        '''website block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#website S3Bucket#website}
        '''
        result = self._values.get("website")
        return typing.cast(typing.Optional["S3BucketWebsite"], result)

    @builtins.property
    def website_domain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#website_domain S3Bucket#website_domain}.'''
        result = self._values.get("website_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_endpoint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#website_endpoint S3Bucket#website_endpoint}.'''
        result = self._values.get("website_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketCorsRule",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_methods": "allowedMethods",
        "allowed_origins": "allowedOrigins",
        "allowed_headers": "allowedHeaders",
        "expose_headers": "exposeHeaders",
        "max_age_seconds": "maxAgeSeconds",
    },
)
class S3BucketCorsRule:
    def __init__(
        self,
        *,
        allowed_methods: typing.Sequence[builtins.str],
        allowed_origins: typing.Sequence[builtins.str],
        allowed_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        expose_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_age_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allowed_methods: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#allowed_methods S3Bucket#allowed_methods}.
        :param allowed_origins: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#allowed_origins S3Bucket#allowed_origins}.
        :param allowed_headers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#allowed_headers S3Bucket#allowed_headers}.
        :param expose_headers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#expose_headers S3Bucket#expose_headers}.
        :param max_age_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#max_age_seconds S3Bucket#max_age_seconds}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "allowed_methods": allowed_methods,
            "allowed_origins": allowed_origins,
        }
        if allowed_headers is not None:
            self._values["allowed_headers"] = allowed_headers
        if expose_headers is not None:
            self._values["expose_headers"] = expose_headers
        if max_age_seconds is not None:
            self._values["max_age_seconds"] = max_age_seconds

    @builtins.property
    def allowed_methods(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#allowed_methods S3Bucket#allowed_methods}.'''
        result = self._values.get("allowed_methods")
        assert result is not None, "Required property 'allowed_methods' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def allowed_origins(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#allowed_origins S3Bucket#allowed_origins}.'''
        result = self._values.get("allowed_origins")
        assert result is not None, "Required property 'allowed_origins' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def allowed_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#allowed_headers S3Bucket#allowed_headers}.'''
        result = self._values.get("allowed_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def expose_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#expose_headers S3Bucket#expose_headers}.'''
        result = self._values.get("expose_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_age_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#max_age_seconds S3Bucket#max_age_seconds}.'''
        result = self._values.get("max_age_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketCorsRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketGrant",
    jsii_struct_bases=[],
    name_mapping={
        "permissions": "permissions",
        "type": "type",
        "id": "id",
        "uri": "uri",
    },
)
class S3BucketGrant:
    def __init__(
        self,
        *,
        permissions: typing.Sequence[builtins.str],
        type: builtins.str,
        id: typing.Optional[builtins.str] = None,
        uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param permissions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#permissions S3Bucket#permissions}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#type S3Bucket#type}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#id S3Bucket#id}.
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#uri S3Bucket#uri}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "permissions": permissions,
            "type": type,
        }
        if id is not None:
            self._values["id"] = id
        if uri is not None:
            self._values["uri"] = uri

    @builtins.property
    def permissions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#permissions S3Bucket#permissions}.'''
        result = self._values.get("permissions")
        assert result is not None, "Required property 'permissions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#type S3Bucket#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#id S3Bucket#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#uri S3Bucket#uri}.'''
        result = self._values.get("uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketGrant(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketIntelligentTieringConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketIntelligentTieringConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration aws_s3_bucket_intelligent_tiering_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        name: builtins.str,
        tiering: typing.Sequence["S3BucketIntelligentTieringConfigurationTiering"],
        filter: typing.Optional["S3BucketIntelligentTieringConfigurationFilter"] = None,
        status: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration aws_s3_bucket_intelligent_tiering_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#bucket S3BucketIntelligentTieringConfiguration#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#name S3BucketIntelligentTieringConfiguration#name}.
        :param tiering: tiering block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#tiering S3BucketIntelligentTieringConfiguration#tiering}
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#filter S3BucketIntelligentTieringConfiguration#filter}
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#status S3BucketIntelligentTieringConfiguration#status}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketIntelligentTieringConfigurationConfig(
            bucket=bucket,
            name=name,
            tiering=tiering,
            filter=filter,
            status=status,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#prefix S3BucketIntelligentTieringConfiguration#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#tags S3BucketIntelligentTieringConfiguration#tags}.
        '''
        value = S3BucketIntelligentTieringConfigurationFilter(prefix=prefix, tags=tags)

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "S3BucketIntelligentTieringConfigurationFilterOutputReference":
        return typing.cast("S3BucketIntelligentTieringConfigurationFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional["S3BucketIntelligentTieringConfigurationFilter"]:
        return typing.cast(typing.Optional["S3BucketIntelligentTieringConfigurationFilter"], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tieringInput")
    def tiering_input(
        self,
    ) -> typing.Optional[typing.List["S3BucketIntelligentTieringConfigurationTiering"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketIntelligentTieringConfigurationTiering"]], jsii.get(self, "tieringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tiering")
    def tiering(self) -> typing.List["S3BucketIntelligentTieringConfigurationTiering"]:
        return typing.cast(typing.List["S3BucketIntelligentTieringConfigurationTiering"], jsii.get(self, "tiering"))

    @tiering.setter
    def tiering(
        self,
        value: typing.List["S3BucketIntelligentTieringConfigurationTiering"],
    ) -> None:
        jsii.set(self, "tiering", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketIntelligentTieringConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "name": "name",
        "tiering": "tiering",
        "filter": "filter",
        "status": "status",
    },
)
class S3BucketIntelligentTieringConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        name: builtins.str,
        tiering: typing.Sequence["S3BucketIntelligentTieringConfigurationTiering"],
        filter: typing.Optional["S3BucketIntelligentTieringConfigurationFilter"] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#bucket S3BucketIntelligentTieringConfiguration#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#name S3BucketIntelligentTieringConfiguration#name}.
        :param tiering: tiering block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#tiering S3BucketIntelligentTieringConfiguration#tiering}
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#filter S3BucketIntelligentTieringConfiguration#filter}
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#status S3BucketIntelligentTieringConfiguration#status}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = S3BucketIntelligentTieringConfigurationFilter(**filter)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "name": name,
            "tiering": tiering,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if filter is not None:
            self._values["filter"] = filter
        if status is not None:
            self._values["status"] = status

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#bucket S3BucketIntelligentTieringConfiguration#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#name S3BucketIntelligentTieringConfiguration#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tiering(self) -> typing.List["S3BucketIntelligentTieringConfigurationTiering"]:
        '''tiering block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#tiering S3BucketIntelligentTieringConfiguration#tiering}
        '''
        result = self._values.get("tiering")
        assert result is not None, "Required property 'tiering' is missing"
        return typing.cast(typing.List["S3BucketIntelligentTieringConfigurationTiering"], result)

    @builtins.property
    def filter(
        self,
    ) -> typing.Optional["S3BucketIntelligentTieringConfigurationFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#filter S3BucketIntelligentTieringConfiguration#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["S3BucketIntelligentTieringConfigurationFilter"], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#status S3BucketIntelligentTieringConfiguration#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketIntelligentTieringConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketIntelligentTieringConfigurationFilter",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix", "tags": "tags"},
)
class S3BucketIntelligentTieringConfigurationFilter:
    def __init__(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#prefix S3BucketIntelligentTieringConfiguration#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#tags S3BucketIntelligentTieringConfiguration#tags}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#prefix S3BucketIntelligentTieringConfiguration#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#tags S3BucketIntelligentTieringConfiguration#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketIntelligentTieringConfigurationFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketIntelligentTieringConfigurationFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketIntelligentTieringConfigurationFilterOutputReference",
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

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketIntelligentTieringConfigurationFilter]:
        return typing.cast(typing.Optional[S3BucketIntelligentTieringConfigurationFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketIntelligentTieringConfigurationFilter],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketIntelligentTieringConfigurationTiering",
    jsii_struct_bases=[],
    name_mapping={"access_tier": "accessTier", "days": "days"},
)
class S3BucketIntelligentTieringConfigurationTiering:
    def __init__(self, *, access_tier: builtins.str, days: jsii.Number) -> None:
        '''
        :param access_tier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#access_tier S3BucketIntelligentTieringConfiguration#access_tier}.
        :param days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#days S3BucketIntelligentTieringConfiguration#days}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "access_tier": access_tier,
            "days": days,
        }

    @builtins.property
    def access_tier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#access_tier S3BucketIntelligentTieringConfiguration#access_tier}.'''
        result = self._values.get("access_tier")
        assert result is not None, "Required property 'access_tier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def days(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_intelligent_tiering_configuration#days S3BucketIntelligentTieringConfiguration#days}.'''
        result = self._values.get("days")
        assert result is not None, "Required property 'days' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketIntelligentTieringConfigurationTiering(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketInventory(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventory",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory aws_s3_bucket_inventory}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        destination: "S3BucketInventoryDestination",
        included_object_versions: builtins.str,
        name: builtins.str,
        schedule: "S3BucketInventorySchedule",
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        filter: typing.Optional["S3BucketInventoryFilter"] = None,
        optional_fields: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory aws_s3_bucket_inventory} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#bucket S3BucketInventory#bucket}.
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#destination S3BucketInventory#destination}
        :param included_object_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#included_object_versions S3BucketInventory#included_object_versions}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#name S3BucketInventory#name}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#schedule S3BucketInventory#schedule}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#enabled S3BucketInventory#enabled}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#filter S3BucketInventory#filter}
        :param optional_fields: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#optional_fields S3BucketInventory#optional_fields}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketInventoryConfig(
            bucket=bucket,
            destination=destination,
            included_object_versions=included_object_versions,
            name=name,
            schedule=schedule,
            enabled=enabled,
            filter=filter,
            optional_fields=optional_fields,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDestination")
    def put_destination(self, *, bucket: "S3BucketInventoryDestinationBucket") -> None:
        '''
        :param bucket: bucket block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#bucket S3BucketInventory#bucket}
        '''
        value = S3BucketInventoryDestination(bucket=bucket)

        return typing.cast(None, jsii.invoke(self, "putDestination", [value]))

    @jsii.member(jsii_name="putFilter")
    def put_filter(self, *, prefix: typing.Optional[builtins.str] = None) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#prefix S3BucketInventory#prefix}.
        '''
        value = S3BucketInventoryFilter(prefix=prefix)

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(self, *, frequency: builtins.str) -> None:
        '''
        :param frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#frequency S3BucketInventory#frequency}.
        '''
        value = S3BucketInventorySchedule(frequency=frequency)

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="resetOptionalFields")
    def reset_optional_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptionalFields", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destination")
    def destination(self) -> "S3BucketInventoryDestinationOutputReference":
        return typing.cast("S3BucketInventoryDestinationOutputReference", jsii.get(self, "destination"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "S3BucketInventoryFilterOutputReference":
        return typing.cast("S3BucketInventoryFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "S3BucketInventoryScheduleOutputReference":
        return typing.cast("S3BucketInventoryScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationInput")
    def destination_input(self) -> typing.Optional["S3BucketInventoryDestination"]:
        return typing.cast(typing.Optional["S3BucketInventoryDestination"], jsii.get(self, "destinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(self) -> typing.Optional["S3BucketInventoryFilter"]:
        return typing.cast(typing.Optional["S3BucketInventoryFilter"], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includedObjectVersionsInput")
    def included_object_versions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "includedObjectVersionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionalFieldsInput")
    def optional_fields_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "optionalFieldsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional["S3BucketInventorySchedule"]:
        return typing.cast(typing.Optional["S3BucketInventorySchedule"], jsii.get(self, "scheduleInput"))

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
    @jsii.member(jsii_name="includedObjectVersions")
    def included_object_versions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "includedObjectVersions"))

    @included_object_versions.setter
    def included_object_versions(self, value: builtins.str) -> None:
        jsii.set(self, "includedObjectVersions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionalFields")
    def optional_fields(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "optionalFields"))

    @optional_fields.setter
    def optional_fields(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "optionalFields", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "destination": "destination",
        "included_object_versions": "includedObjectVersions",
        "name": "name",
        "schedule": "schedule",
        "enabled": "enabled",
        "filter": "filter",
        "optional_fields": "optionalFields",
    },
)
class S3BucketInventoryConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        destination: "S3BucketInventoryDestination",
        included_object_versions: builtins.str,
        name: builtins.str,
        schedule: "S3BucketInventorySchedule",
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        filter: typing.Optional["S3BucketInventoryFilter"] = None,
        optional_fields: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#bucket S3BucketInventory#bucket}.
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#destination S3BucketInventory#destination}
        :param included_object_versions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#included_object_versions S3BucketInventory#included_object_versions}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#name S3BucketInventory#name}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#schedule S3BucketInventory#schedule}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#enabled S3BucketInventory#enabled}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#filter S3BucketInventory#filter}
        :param optional_fields: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#optional_fields S3BucketInventory#optional_fields}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(destination, dict):
            destination = S3BucketInventoryDestination(**destination)
        if isinstance(schedule, dict):
            schedule = S3BucketInventorySchedule(**schedule)
        if isinstance(filter, dict):
            filter = S3BucketInventoryFilter(**filter)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "destination": destination,
            "included_object_versions": included_object_versions,
            "name": name,
            "schedule": schedule,
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
        if filter is not None:
            self._values["filter"] = filter
        if optional_fields is not None:
            self._values["optional_fields"] = optional_fields

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#bucket S3BucketInventory#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def destination(self) -> "S3BucketInventoryDestination":
        '''destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#destination S3BucketInventory#destination}
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("S3BucketInventoryDestination", result)

    @builtins.property
    def included_object_versions(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#included_object_versions S3BucketInventory#included_object_versions}.'''
        result = self._values.get("included_object_versions")
        assert result is not None, "Required property 'included_object_versions' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#name S3BucketInventory#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schedule(self) -> "S3BucketInventorySchedule":
        '''schedule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#schedule S3BucketInventory#schedule}
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast("S3BucketInventorySchedule", result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#enabled S3BucketInventory#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def filter(self) -> typing.Optional["S3BucketInventoryFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#filter S3BucketInventory#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["S3BucketInventoryFilter"], result)

    @builtins.property
    def optional_fields(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#optional_fields S3BucketInventory#optional_fields}.'''
        result = self._values.get("optional_fields")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketInventoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestination",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket"},
)
class S3BucketInventoryDestination:
    def __init__(self, *, bucket: "S3BucketInventoryDestinationBucket") -> None:
        '''
        :param bucket: bucket block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#bucket S3BucketInventory#bucket}
        '''
        if isinstance(bucket, dict):
            bucket = S3BucketInventoryDestinationBucket(**bucket)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }

    @builtins.property
    def bucket(self) -> "S3BucketInventoryDestinationBucket":
        '''bucket block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#bucket S3BucketInventory#bucket}
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast("S3BucketInventoryDestinationBucket", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketInventoryDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestinationBucket",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_arn": "bucketArn",
        "format": "format",
        "account_id": "accountId",
        "encryption": "encryption",
        "prefix": "prefix",
    },
)
class S3BucketInventoryDestinationBucket:
    def __init__(
        self,
        *,
        bucket_arn: builtins.str,
        format: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        encryption: typing.Optional["S3BucketInventoryDestinationBucketEncryption"] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#bucket_arn S3BucketInventory#bucket_arn}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#format S3BucketInventory#format}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#account_id S3BucketInventory#account_id}.
        :param encryption: encryption block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#encryption S3BucketInventory#encryption}
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#prefix S3BucketInventory#prefix}.
        '''
        if isinstance(encryption, dict):
            encryption = S3BucketInventoryDestinationBucketEncryption(**encryption)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_arn": bucket_arn,
            "format": format,
        }
        if account_id is not None:
            self._values["account_id"] = account_id
        if encryption is not None:
            self._values["encryption"] = encryption
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def bucket_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#bucket_arn S3BucketInventory#bucket_arn}.'''
        result = self._values.get("bucket_arn")
        assert result is not None, "Required property 'bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def format(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#format S3BucketInventory#format}.'''
        result = self._values.get("format")
        assert result is not None, "Required property 'format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#account_id S3BucketInventory#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption(
        self,
    ) -> typing.Optional["S3BucketInventoryDestinationBucketEncryption"]:
        '''encryption block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#encryption S3BucketInventory#encryption}
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional["S3BucketInventoryDestinationBucketEncryption"], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#prefix S3BucketInventory#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketInventoryDestinationBucket(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestinationBucketEncryption",
    jsii_struct_bases=[],
    name_mapping={"sse_kms": "sseKms", "sse_s3": "sseS3"},
)
class S3BucketInventoryDestinationBucketEncryption:
    def __init__(
        self,
        *,
        sse_kms: typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseKms"] = None,
        sse_s3: typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseS3"] = None,
    ) -> None:
        '''
        :param sse_kms: sse_kms block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#sse_kms S3BucketInventory#sse_kms}
        :param sse_s3: sse_s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#sse_s3 S3BucketInventory#sse_s3}
        '''
        if isinstance(sse_kms, dict):
            sse_kms = S3BucketInventoryDestinationBucketEncryptionSseKms(**sse_kms)
        if isinstance(sse_s3, dict):
            sse_s3 = S3BucketInventoryDestinationBucketEncryptionSseS3(**sse_s3)
        self._values: typing.Dict[str, typing.Any] = {}
        if sse_kms is not None:
            self._values["sse_kms"] = sse_kms
        if sse_s3 is not None:
            self._values["sse_s3"] = sse_s3

    @builtins.property
    def sse_kms(
        self,
    ) -> typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseKms"]:
        '''sse_kms block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#sse_kms S3BucketInventory#sse_kms}
        '''
        result = self._values.get("sse_kms")
        return typing.cast(typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseKms"], result)

    @builtins.property
    def sse_s3(
        self,
    ) -> typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseS3"]:
        '''sse_s3 block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#sse_s3 S3BucketInventory#sse_s3}
        '''
        result = self._values.get("sse_s3")
        return typing.cast(typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseS3"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketInventoryDestinationBucketEncryption(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketInventoryDestinationBucketEncryptionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestinationBucketEncryptionOutputReference",
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

    @jsii.member(jsii_name="putSseKms")
    def put_sse_kms(self, *, key_id: builtins.str) -> None:
        '''
        :param key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#key_id S3BucketInventory#key_id}.
        '''
        value = S3BucketInventoryDestinationBucketEncryptionSseKms(key_id=key_id)

        return typing.cast(None, jsii.invoke(self, "putSseKms", [value]))

    @jsii.member(jsii_name="putSseS3")
    def put_sse_s3(self) -> None:
        value = S3BucketInventoryDestinationBucketEncryptionSseS3()

        return typing.cast(None, jsii.invoke(self, "putSseS3", [value]))

    @jsii.member(jsii_name="resetSseKms")
    def reset_sse_kms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSseKms", []))

    @jsii.member(jsii_name="resetSseS3")
    def reset_sse_s3(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSseS3", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseKms")
    def sse_kms(
        self,
    ) -> "S3BucketInventoryDestinationBucketEncryptionSseKmsOutputReference":
        return typing.cast("S3BucketInventoryDestinationBucketEncryptionSseKmsOutputReference", jsii.get(self, "sseKms"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseS3")
    def sse_s3(
        self,
    ) -> "S3BucketInventoryDestinationBucketEncryptionSseS3OutputReference":
        return typing.cast("S3BucketInventoryDestinationBucketEncryptionSseS3OutputReference", jsii.get(self, "sseS3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseKmsInput")
    def sse_kms_input(
        self,
    ) -> typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseKms"]:
        return typing.cast(typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseKms"], jsii.get(self, "sseKmsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseS3Input")
    def sse_s3_input(
        self,
    ) -> typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseS3"]:
        return typing.cast(typing.Optional["S3BucketInventoryDestinationBucketEncryptionSseS3"], jsii.get(self, "sseS3Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketInventoryDestinationBucketEncryption]:
        return typing.cast(typing.Optional[S3BucketInventoryDestinationBucketEncryption], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketInventoryDestinationBucketEncryption],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestinationBucketEncryptionSseKms",
    jsii_struct_bases=[],
    name_mapping={"key_id": "keyId"},
)
class S3BucketInventoryDestinationBucketEncryptionSseKms:
    def __init__(self, *, key_id: builtins.str) -> None:
        '''
        :param key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#key_id S3BucketInventory#key_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key_id": key_id,
        }

    @builtins.property
    def key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#key_id S3BucketInventory#key_id}.'''
        result = self._values.get("key_id")
        assert result is not None, "Required property 'key_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketInventoryDestinationBucketEncryptionSseKms(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketInventoryDestinationBucketEncryptionSseKmsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestinationBucketEncryptionSseKmsOutputReference",
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
    @jsii.member(jsii_name="keyIdInput")
    def key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @key_id.setter
    def key_id(self, value: builtins.str) -> None:
        jsii.set(self, "keyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketInventoryDestinationBucketEncryptionSseKms]:
        return typing.cast(typing.Optional[S3BucketInventoryDestinationBucketEncryptionSseKms], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketInventoryDestinationBucketEncryptionSseKms],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestinationBucketEncryptionSseS3",
    jsii_struct_bases=[],
    name_mapping={},
)
class S3BucketInventoryDestinationBucketEncryptionSseS3:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketInventoryDestinationBucketEncryptionSseS3(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketInventoryDestinationBucketEncryptionSseS3OutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestinationBucketEncryptionSseS3OutputReference",
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
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketInventoryDestinationBucketEncryptionSseS3]:
        return typing.cast(typing.Optional[S3BucketInventoryDestinationBucketEncryptionSseS3], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketInventoryDestinationBucketEncryptionSseS3],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketInventoryDestinationBucketOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestinationBucketOutputReference",
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

    @jsii.member(jsii_name="putEncryption")
    def put_encryption(
        self,
        *,
        sse_kms: typing.Optional[S3BucketInventoryDestinationBucketEncryptionSseKms] = None,
        sse_s3: typing.Optional[S3BucketInventoryDestinationBucketEncryptionSseS3] = None,
    ) -> None:
        '''
        :param sse_kms: sse_kms block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#sse_kms S3BucketInventory#sse_kms}
        :param sse_s3: sse_s3 block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#sse_s3 S3BucketInventory#sse_s3}
        '''
        value = S3BucketInventoryDestinationBucketEncryption(
            sse_kms=sse_kms, sse_s3=sse_s3
        )

        return typing.cast(None, jsii.invoke(self, "putEncryption", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetEncryption")
    def reset_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryption", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryption")
    def encryption(self) -> S3BucketInventoryDestinationBucketEncryptionOutputReference:
        return typing.cast(S3BucketInventoryDestinationBucketEncryptionOutputReference, jsii.get(self, "encryption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketArnInput")
    def bucket_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionInput")
    def encryption_input(
        self,
    ) -> typing.Optional[S3BucketInventoryDestinationBucketEncryption]:
        return typing.cast(typing.Optional[S3BucketInventoryDestinationBucketEncryption], jsii.get(self, "encryptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketArn")
    def bucket_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketArn"))

    @bucket_arn.setter
    def bucket_arn(self, value: builtins.str) -> None:
        jsii.set(self, "bucketArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        jsii.set(self, "format", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketInventoryDestinationBucket]:
        return typing.cast(typing.Optional[S3BucketInventoryDestinationBucket], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketInventoryDestinationBucket],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketInventoryDestinationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryDestinationOutputReference",
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

    @jsii.member(jsii_name="putBucket")
    def put_bucket(
        self,
        *,
        bucket_arn: builtins.str,
        format: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[S3BucketInventoryDestinationBucketEncryption] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#bucket_arn S3BucketInventory#bucket_arn}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#format S3BucketInventory#format}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#account_id S3BucketInventory#account_id}.
        :param encryption: encryption block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#encryption S3BucketInventory#encryption}
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#prefix S3BucketInventory#prefix}.
        '''
        value = S3BucketInventoryDestinationBucket(
            bucket_arn=bucket_arn,
            format=format,
            account_id=account_id,
            encryption=encryption,
            prefix=prefix,
        )

        return typing.cast(None, jsii.invoke(self, "putBucket", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> S3BucketInventoryDestinationBucketOutputReference:
        return typing.cast(S3BucketInventoryDestinationBucketOutputReference, jsii.get(self, "bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[S3BucketInventoryDestinationBucket]:
        return typing.cast(typing.Optional[S3BucketInventoryDestinationBucket], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketInventoryDestination]:
        return typing.cast(typing.Optional[S3BucketInventoryDestination], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketInventoryDestination],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryFilter",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix"},
)
class S3BucketInventoryFilter:
    def __init__(self, *, prefix: typing.Optional[builtins.str] = None) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#prefix S3BucketInventory#prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#prefix S3BucketInventory#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketInventoryFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketInventoryFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryFilterOutputReference",
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

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketInventoryFilter]:
        return typing.cast(typing.Optional[S3BucketInventoryFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[S3BucketInventoryFilter]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventorySchedule",
    jsii_struct_bases=[],
    name_mapping={"frequency": "frequency"},
)
class S3BucketInventorySchedule:
    def __init__(self, *, frequency: builtins.str) -> None:
        '''
        :param frequency: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#frequency S3BucketInventory#frequency}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "frequency": frequency,
        }

    @builtins.property
    def frequency(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_inventory#frequency S3BucketInventory#frequency}.'''
        result = self._values.get("frequency")
        assert result is not None, "Required property 'frequency' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketInventorySchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketInventoryScheduleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketInventoryScheduleOutputReference",
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
    @jsii.member(jsii_name="frequencyInput")
    def frequency_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frequencyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        jsii.set(self, "frequency", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketInventorySchedule]:
        return typing.cast(typing.Optional[S3BucketInventorySchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[S3BucketInventorySchedule]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketLifecycleRule",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "abort_incomplete_multipart_upload_days": "abortIncompleteMultipartUploadDays",
        "expiration": "expiration",
        "id": "id",
        "noncurrent_version_expiration": "noncurrentVersionExpiration",
        "noncurrent_version_transition": "noncurrentVersionTransition",
        "prefix": "prefix",
        "tags": "tags",
        "transition": "transition",
    },
)
class S3BucketLifecycleRule:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        abort_incomplete_multipart_upload_days: typing.Optional[jsii.Number] = None,
        expiration: typing.Optional["S3BucketLifecycleRuleExpiration"] = None,
        id: typing.Optional[builtins.str] = None,
        noncurrent_version_expiration: typing.Optional["S3BucketLifecycleRuleNoncurrentVersionExpiration"] = None,
        noncurrent_version_transition: typing.Optional[typing.Sequence["S3BucketLifecycleRuleNoncurrentVersionTransition"]] = None,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        transition: typing.Optional[typing.Sequence["S3BucketLifecycleRuleTransition"]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#enabled S3Bucket#enabled}.
        :param abort_incomplete_multipart_upload_days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#abort_incomplete_multipart_upload_days S3Bucket#abort_incomplete_multipart_upload_days}.
        :param expiration: expiration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#expiration S3Bucket#expiration}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#id S3Bucket#id}.
        :param noncurrent_version_expiration: noncurrent_version_expiration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#noncurrent_version_expiration S3Bucket#noncurrent_version_expiration}
        :param noncurrent_version_transition: noncurrent_version_transition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#noncurrent_version_transition S3Bucket#noncurrent_version_transition}
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#prefix S3Bucket#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags S3Bucket#tags}.
        :param transition: transition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#transition S3Bucket#transition}
        '''
        if isinstance(expiration, dict):
            expiration = S3BucketLifecycleRuleExpiration(**expiration)
        if isinstance(noncurrent_version_expiration, dict):
            noncurrent_version_expiration = S3BucketLifecycleRuleNoncurrentVersionExpiration(**noncurrent_version_expiration)
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }
        if abort_incomplete_multipart_upload_days is not None:
            self._values["abort_incomplete_multipart_upload_days"] = abort_incomplete_multipart_upload_days
        if expiration is not None:
            self._values["expiration"] = expiration
        if id is not None:
            self._values["id"] = id
        if noncurrent_version_expiration is not None:
            self._values["noncurrent_version_expiration"] = noncurrent_version_expiration
        if noncurrent_version_transition is not None:
            self._values["noncurrent_version_transition"] = noncurrent_version_transition
        if prefix is not None:
            self._values["prefix"] = prefix
        if tags is not None:
            self._values["tags"] = tags
        if transition is not None:
            self._values["transition"] = transition

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#enabled S3Bucket#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def abort_incomplete_multipart_upload_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#abort_incomplete_multipart_upload_days S3Bucket#abort_incomplete_multipart_upload_days}.'''
        result = self._values.get("abort_incomplete_multipart_upload_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def expiration(self) -> typing.Optional["S3BucketLifecycleRuleExpiration"]:
        '''expiration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#expiration S3Bucket#expiration}
        '''
        result = self._values.get("expiration")
        return typing.cast(typing.Optional["S3BucketLifecycleRuleExpiration"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#id S3Bucket#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def noncurrent_version_expiration(
        self,
    ) -> typing.Optional["S3BucketLifecycleRuleNoncurrentVersionExpiration"]:
        '''noncurrent_version_expiration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#noncurrent_version_expiration S3Bucket#noncurrent_version_expiration}
        '''
        result = self._values.get("noncurrent_version_expiration")
        return typing.cast(typing.Optional["S3BucketLifecycleRuleNoncurrentVersionExpiration"], result)

    @builtins.property
    def noncurrent_version_transition(
        self,
    ) -> typing.Optional[typing.List["S3BucketLifecycleRuleNoncurrentVersionTransition"]]:
        '''noncurrent_version_transition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#noncurrent_version_transition S3Bucket#noncurrent_version_transition}
        '''
        result = self._values.get("noncurrent_version_transition")
        return typing.cast(typing.Optional[typing.List["S3BucketLifecycleRuleNoncurrentVersionTransition"]], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#prefix S3Bucket#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags S3Bucket#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def transition(
        self,
    ) -> typing.Optional[typing.List["S3BucketLifecycleRuleTransition"]]:
        '''transition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#transition S3Bucket#transition}
        '''
        result = self._values.get("transition")
        return typing.cast(typing.Optional[typing.List["S3BucketLifecycleRuleTransition"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketLifecycleRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketLifecycleRuleExpiration",
    jsii_struct_bases=[],
    name_mapping={
        "date": "date",
        "days": "days",
        "expired_object_delete_marker": "expiredObjectDeleteMarker",
    },
)
class S3BucketLifecycleRuleExpiration:
    def __init__(
        self,
        *,
        date: typing.Optional[builtins.str] = None,
        days: typing.Optional[jsii.Number] = None,
        expired_object_delete_marker: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param date: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#date S3Bucket#date}.
        :param days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.
        :param expired_object_delete_marker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#expired_object_delete_marker S3Bucket#expired_object_delete_marker}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if date is not None:
            self._values["date"] = date
        if days is not None:
            self._values["days"] = days
        if expired_object_delete_marker is not None:
            self._values["expired_object_delete_marker"] = expired_object_delete_marker

    @builtins.property
    def date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#date S3Bucket#date}.'''
        result = self._values.get("date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.'''
        result = self._values.get("days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def expired_object_delete_marker(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#expired_object_delete_marker S3Bucket#expired_object_delete_marker}.'''
        result = self._values.get("expired_object_delete_marker")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketLifecycleRuleExpiration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketLifecycleRuleExpirationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketLifecycleRuleExpirationOutputReference",
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

    @jsii.member(jsii_name="resetDate")
    def reset_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDate", []))

    @jsii.member(jsii_name="resetDays")
    def reset_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDays", []))

    @jsii.member(jsii_name="resetExpiredObjectDeleteMarker")
    def reset_expired_object_delete_marker(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpiredObjectDeleteMarker", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateInput")
    def date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="daysInput")
    def days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "daysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expiredObjectDeleteMarkerInput")
    def expired_object_delete_marker_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "expiredObjectDeleteMarkerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="date")
    def date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "date"))

    @date.setter
    def date(self, value: builtins.str) -> None:
        jsii.set(self, "date", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="days")
    def days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "days"))

    @days.setter
    def days(self, value: jsii.Number) -> None:
        jsii.set(self, "days", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expiredObjectDeleteMarker")
    def expired_object_delete_marker(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "expiredObjectDeleteMarker"))

    @expired_object_delete_marker.setter
    def expired_object_delete_marker(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "expiredObjectDeleteMarker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketLifecycleRuleExpiration]:
        return typing.cast(typing.Optional[S3BucketLifecycleRuleExpiration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketLifecycleRuleExpiration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketLifecycleRuleNoncurrentVersionExpiration",
    jsii_struct_bases=[],
    name_mapping={"days": "days"},
)
class S3BucketLifecycleRuleNoncurrentVersionExpiration:
    def __init__(self, *, days: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if days is not None:
            self._values["days"] = days

    @builtins.property
    def days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.'''
        result = self._values.get("days")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketLifecycleRuleNoncurrentVersionExpiration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketLifecycleRuleNoncurrentVersionExpirationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketLifecycleRuleNoncurrentVersionExpirationOutputReference",
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

    @jsii.member(jsii_name="resetDays")
    def reset_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDays", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="daysInput")
    def days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "daysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="days")
    def days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "days"))

    @days.setter
    def days(self, value: jsii.Number) -> None:
        jsii.set(self, "days", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketLifecycleRuleNoncurrentVersionExpiration]:
        return typing.cast(typing.Optional[S3BucketLifecycleRuleNoncurrentVersionExpiration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketLifecycleRuleNoncurrentVersionExpiration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketLifecycleRuleNoncurrentVersionTransition",
    jsii_struct_bases=[],
    name_mapping={"storage_class": "storageClass", "days": "days"},
)
class S3BucketLifecycleRuleNoncurrentVersionTransition:
    def __init__(
        self,
        *,
        storage_class: builtins.str,
        days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#storage_class S3Bucket#storage_class}.
        :param days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "storage_class": storage_class,
        }
        if days is not None:
            self._values["days"] = days

    @builtins.property
    def storage_class(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#storage_class S3Bucket#storage_class}.'''
        result = self._values.get("storage_class")
        assert result is not None, "Required property 'storage_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.'''
        result = self._values.get("days")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketLifecycleRuleNoncurrentVersionTransition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketLifecycleRuleTransition",
    jsii_struct_bases=[],
    name_mapping={"storage_class": "storageClass", "date": "date", "days": "days"},
)
class S3BucketLifecycleRuleTransition:
    def __init__(
        self,
        *,
        storage_class: builtins.str,
        date: typing.Optional[builtins.str] = None,
        days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#storage_class S3Bucket#storage_class}.
        :param date: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#date S3Bucket#date}.
        :param days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "storage_class": storage_class,
        }
        if date is not None:
            self._values["date"] = date
        if days is not None:
            self._values["days"] = days

    @builtins.property
    def storage_class(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#storage_class S3Bucket#storage_class}.'''
        result = self._values.get("storage_class")
        assert result is not None, "Required property 'storage_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#date S3Bucket#date}.'''
        result = self._values.get("date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.'''
        result = self._values.get("days")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketLifecycleRuleTransition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketLogging",
    jsii_struct_bases=[],
    name_mapping={"target_bucket": "targetBucket", "target_prefix": "targetPrefix"},
)
class S3BucketLogging:
    def __init__(
        self,
        *,
        target_bucket: builtins.str,
        target_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target_bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#target_bucket S3Bucket#target_bucket}.
        :param target_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#target_prefix S3Bucket#target_prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_bucket": target_bucket,
        }
        if target_prefix is not None:
            self._values["target_prefix"] = target_prefix

    @builtins.property
    def target_bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#target_bucket S3Bucket#target_bucket}.'''
        result = self._values.get("target_bucket")
        assert result is not None, "Required property 'target_bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#target_prefix S3Bucket#target_prefix}.'''
        result = self._values.get("target_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketLogging(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketMetric(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketMetric",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric aws_s3_bucket_metric}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        name: builtins.str,
        filter: typing.Optional["S3BucketMetricFilter"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric aws_s3_bucket_metric} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#bucket S3BucketMetric#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#name S3BucketMetric#name}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#filter S3BucketMetric#filter}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketMetricConfig(
            bucket=bucket,
            name=name,
            filter=filter,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#prefix S3BucketMetric#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#tags S3BucketMetric#tags}.
        '''
        value = S3BucketMetricFilter(prefix=prefix, tags=tags)

        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

    @jsii.member(jsii_name="resetFilter")
    def reset_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilter", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> "S3BucketMetricFilterOutputReference":
        return typing.cast("S3BucketMetricFilterOutputReference", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(self) -> typing.Optional["S3BucketMetricFilter"]:
        return typing.cast(typing.Optional["S3BucketMetricFilter"], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketMetricConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "name": "name",
        "filter": "filter",
    },
)
class S3BucketMetricConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        name: builtins.str,
        filter: typing.Optional["S3BucketMetricFilter"] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#bucket S3BucketMetric#bucket}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#name S3BucketMetric#name}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#filter S3BucketMetric#filter}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(filter, dict):
            filter = S3BucketMetricFilter(**filter)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
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
        if filter is not None:
            self._values["filter"] = filter

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#bucket S3BucketMetric#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#name S3BucketMetric#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(self) -> typing.Optional["S3BucketMetricFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#filter S3BucketMetric#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["S3BucketMetricFilter"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketMetricConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketMetricFilter",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix", "tags": "tags"},
)
class S3BucketMetricFilter:
    def __init__(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#prefix S3BucketMetric#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#tags S3BucketMetric#tags}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#prefix S3BucketMetric#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_metric#tags S3BucketMetric#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketMetricFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketMetricFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketMetricFilterOutputReference",
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

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketMetricFilter]:
        return typing.cast(typing.Optional[S3BucketMetricFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[S3BucketMetricFilter]) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketNotification(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketNotification",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification aws_s3_bucket_notification}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        lambda_function: typing.Optional[typing.Sequence["S3BucketNotificationLambdaFunction"]] = None,
        queue: typing.Optional[typing.Sequence["S3BucketNotificationQueue"]] = None,
        topic: typing.Optional[typing.Sequence["S3BucketNotificationTopic"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification aws_s3_bucket_notification} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#bucket S3BucketNotification#bucket}.
        :param lambda_function: lambda_function block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#lambda_function S3BucketNotification#lambda_function}
        :param queue: queue block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#queue S3BucketNotification#queue}
        :param topic: topic block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#topic S3BucketNotification#topic}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketNotificationConfig(
            bucket=bucket,
            lambda_function=lambda_function,
            queue=queue,
            topic=topic,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetLambdaFunction")
    def reset_lambda_function(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambdaFunction", []))

    @jsii.member(jsii_name="resetQueue")
    def reset_queue(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueue", []))

    @jsii.member(jsii_name="resetTopic")
    def reset_topic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopic", []))

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
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunctionInput")
    def lambda_function_input(
        self,
    ) -> typing.Optional[typing.List["S3BucketNotificationLambdaFunction"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketNotificationLambdaFunction"]], jsii.get(self, "lambdaFunctionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queueInput")
    def queue_input(self) -> typing.Optional[typing.List["S3BucketNotificationQueue"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketNotificationQueue"]], jsii.get(self, "queueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicInput")
    def topic_input(self) -> typing.Optional[typing.List["S3BucketNotificationTopic"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketNotificationTopic"]], jsii.get(self, "topicInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> typing.List["S3BucketNotificationLambdaFunction"]:
        return typing.cast(typing.List["S3BucketNotificationLambdaFunction"], jsii.get(self, "lambdaFunction"))

    @lambda_function.setter
    def lambda_function(
        self,
        value: typing.List["S3BucketNotificationLambdaFunction"],
    ) -> None:
        jsii.set(self, "lambdaFunction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queue")
    def queue(self) -> typing.List["S3BucketNotificationQueue"]:
        return typing.cast(typing.List["S3BucketNotificationQueue"], jsii.get(self, "queue"))

    @queue.setter
    def queue(self, value: typing.List["S3BucketNotificationQueue"]) -> None:
        jsii.set(self, "queue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topic")
    def topic(self) -> typing.List["S3BucketNotificationTopic"]:
        return typing.cast(typing.List["S3BucketNotificationTopic"], jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: typing.List["S3BucketNotificationTopic"]) -> None:
        jsii.set(self, "topic", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketNotificationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "lambda_function": "lambdaFunction",
        "queue": "queue",
        "topic": "topic",
    },
)
class S3BucketNotificationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        lambda_function: typing.Optional[typing.Sequence["S3BucketNotificationLambdaFunction"]] = None,
        queue: typing.Optional[typing.Sequence["S3BucketNotificationQueue"]] = None,
        topic: typing.Optional[typing.Sequence["S3BucketNotificationTopic"]] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#bucket S3BucketNotification#bucket}.
        :param lambda_function: lambda_function block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#lambda_function S3BucketNotification#lambda_function}
        :param queue: queue block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#queue S3BucketNotification#queue}
        :param topic: topic block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#topic S3BucketNotification#topic}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if lambda_function is not None:
            self._values["lambda_function"] = lambda_function
        if queue is not None:
            self._values["queue"] = queue
        if topic is not None:
            self._values["topic"] = topic

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#bucket S3BucketNotification#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_function(
        self,
    ) -> typing.Optional[typing.List["S3BucketNotificationLambdaFunction"]]:
        '''lambda_function block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#lambda_function S3BucketNotification#lambda_function}
        '''
        result = self._values.get("lambda_function")
        return typing.cast(typing.Optional[typing.List["S3BucketNotificationLambdaFunction"]], result)

    @builtins.property
    def queue(self) -> typing.Optional[typing.List["S3BucketNotificationQueue"]]:
        '''queue block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#queue S3BucketNotification#queue}
        '''
        result = self._values.get("queue")
        return typing.cast(typing.Optional[typing.List["S3BucketNotificationQueue"]], result)

    @builtins.property
    def topic(self) -> typing.Optional[typing.List["S3BucketNotificationTopic"]]:
        '''topic block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#topic S3BucketNotification#topic}
        '''
        result = self._values.get("topic")
        return typing.cast(typing.Optional[typing.List["S3BucketNotificationTopic"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketNotificationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketNotificationLambdaFunction",
    jsii_struct_bases=[],
    name_mapping={
        "events": "events",
        "filter_prefix": "filterPrefix",
        "filter_suffix": "filterSuffix",
        "id": "id",
        "lambda_function_arn": "lambdaFunctionArn",
    },
)
class S3BucketNotificationLambdaFunction:
    def __init__(
        self,
        *,
        events: typing.Sequence[builtins.str],
        filter_prefix: typing.Optional[builtins.str] = None,
        filter_suffix: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        lambda_function_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#events S3BucketNotification#events}.
        :param filter_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_prefix S3BucketNotification#filter_prefix}.
        :param filter_suffix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_suffix S3BucketNotification#filter_suffix}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#id S3BucketNotification#id}.
        :param lambda_function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#lambda_function_arn S3BucketNotification#lambda_function_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "events": events,
        }
        if filter_prefix is not None:
            self._values["filter_prefix"] = filter_prefix
        if filter_suffix is not None:
            self._values["filter_suffix"] = filter_suffix
        if id is not None:
            self._values["id"] = id
        if lambda_function_arn is not None:
            self._values["lambda_function_arn"] = lambda_function_arn

    @builtins.property
    def events(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#events S3BucketNotification#events}.'''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def filter_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_prefix S3BucketNotification#filter_prefix}.'''
        result = self._values.get("filter_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filter_suffix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_suffix S3BucketNotification#filter_suffix}.'''
        result = self._values.get("filter_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#id S3BucketNotification#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_function_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#lambda_function_arn S3BucketNotification#lambda_function_arn}.'''
        result = self._values.get("lambda_function_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketNotificationLambdaFunction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketNotificationQueue",
    jsii_struct_bases=[],
    name_mapping={
        "events": "events",
        "queue_arn": "queueArn",
        "filter_prefix": "filterPrefix",
        "filter_suffix": "filterSuffix",
        "id": "id",
    },
)
class S3BucketNotificationQueue:
    def __init__(
        self,
        *,
        events: typing.Sequence[builtins.str],
        queue_arn: builtins.str,
        filter_prefix: typing.Optional[builtins.str] = None,
        filter_suffix: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#events S3BucketNotification#events}.
        :param queue_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#queue_arn S3BucketNotification#queue_arn}.
        :param filter_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_prefix S3BucketNotification#filter_prefix}.
        :param filter_suffix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_suffix S3BucketNotification#filter_suffix}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#id S3BucketNotification#id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "events": events,
            "queue_arn": queue_arn,
        }
        if filter_prefix is not None:
            self._values["filter_prefix"] = filter_prefix
        if filter_suffix is not None:
            self._values["filter_suffix"] = filter_suffix
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def events(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#events S3BucketNotification#events}.'''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def queue_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#queue_arn S3BucketNotification#queue_arn}.'''
        result = self._values.get("queue_arn")
        assert result is not None, "Required property 'queue_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_prefix S3BucketNotification#filter_prefix}.'''
        result = self._values.get("filter_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filter_suffix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_suffix S3BucketNotification#filter_suffix}.'''
        result = self._values.get("filter_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#id S3BucketNotification#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketNotificationQueue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketNotificationTopic",
    jsii_struct_bases=[],
    name_mapping={
        "events": "events",
        "topic_arn": "topicArn",
        "filter_prefix": "filterPrefix",
        "filter_suffix": "filterSuffix",
        "id": "id",
    },
)
class S3BucketNotificationTopic:
    def __init__(
        self,
        *,
        events: typing.Sequence[builtins.str],
        topic_arn: builtins.str,
        filter_prefix: typing.Optional[builtins.str] = None,
        filter_suffix: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param events: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#events S3BucketNotification#events}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#topic_arn S3BucketNotification#topic_arn}.
        :param filter_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_prefix S3BucketNotification#filter_prefix}.
        :param filter_suffix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_suffix S3BucketNotification#filter_suffix}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#id S3BucketNotification#id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "events": events,
            "topic_arn": topic_arn,
        }
        if filter_prefix is not None:
            self._values["filter_prefix"] = filter_prefix
        if filter_suffix is not None:
            self._values["filter_suffix"] = filter_suffix
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def events(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#events S3BucketNotification#events}.'''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def topic_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#topic_arn S3BucketNotification#topic_arn}.'''
        result = self._values.get("topic_arn")
        assert result is not None, "Required property 'topic_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_prefix S3BucketNotification#filter_prefix}.'''
        result = self._values.get("filter_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filter_suffix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#filter_suffix S3BucketNotification#filter_suffix}.'''
        result = self._values.get("filter_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_notification#id S3BucketNotification#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketNotificationTopic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketObject(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketObject",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object aws_s3_bucket_object}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        key: builtins.str,
        acl: typing.Optional[builtins.str] = None,
        bucket_key_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cache_control: typing.Optional[builtins.str] = None,
        content: typing.Optional[builtins.str] = None,
        content_base64: typing.Optional[builtins.str] = None,
        content_disposition: typing.Optional[builtins.str] = None,
        content_encoding: typing.Optional[builtins.str] = None,
        content_language: typing.Optional[builtins.str] = None,
        content_type: typing.Optional[builtins.str] = None,
        etag: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        object_lock_legal_hold_status: typing.Optional[builtins.str] = None,
        object_lock_mode: typing.Optional[builtins.str] = None,
        object_lock_retain_until_date: typing.Optional[builtins.str] = None,
        server_side_encryption: typing.Optional[builtins.str] = None,
        source: typing.Optional[builtins.str] = None,
        source_hash: typing.Optional[builtins.str] = None,
        storage_class: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        website_redirect: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object aws_s3_bucket_object} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#bucket S3BucketObject#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#key S3BucketObject#key}.
        :param acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#acl S3BucketObject#acl}.
        :param bucket_key_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#bucket_key_enabled S3BucketObject#bucket_key_enabled}.
        :param cache_control: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#cache_control S3BucketObject#cache_control}.
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content S3BucketObject#content}.
        :param content_base64: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_base64 S3BucketObject#content_base64}.
        :param content_disposition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_disposition S3BucketObject#content_disposition}.
        :param content_encoding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_encoding S3BucketObject#content_encoding}.
        :param content_language: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_language S3BucketObject#content_language}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_type S3BucketObject#content_type}.
        :param etag: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#etag S3BucketObject#etag}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#force_destroy S3BucketObject#force_destroy}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#kms_key_id S3BucketObject#kms_key_id}.
        :param metadata: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#metadata S3BucketObject#metadata}.
        :param object_lock_legal_hold_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#object_lock_legal_hold_status S3BucketObject#object_lock_legal_hold_status}.
        :param object_lock_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#object_lock_mode S3BucketObject#object_lock_mode}.
        :param object_lock_retain_until_date: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#object_lock_retain_until_date S3BucketObject#object_lock_retain_until_date}.
        :param server_side_encryption: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#server_side_encryption S3BucketObject#server_side_encryption}.
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#source S3BucketObject#source}.
        :param source_hash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#source_hash S3BucketObject#source_hash}.
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#storage_class S3BucketObject#storage_class}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#tags S3BucketObject#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#tags_all S3BucketObject#tags_all}.
        :param website_redirect: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#website_redirect S3BucketObject#website_redirect}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketObjectConfig(
            bucket=bucket,
            key=key,
            acl=acl,
            bucket_key_enabled=bucket_key_enabled,
            cache_control=cache_control,
            content=content,
            content_base64=content_base64,
            content_disposition=content_disposition,
            content_encoding=content_encoding,
            content_language=content_language,
            content_type=content_type,
            etag=etag,
            force_destroy=force_destroy,
            kms_key_id=kms_key_id,
            metadata=metadata,
            object_lock_legal_hold_status=object_lock_legal_hold_status,
            object_lock_mode=object_lock_mode,
            object_lock_retain_until_date=object_lock_retain_until_date,
            server_side_encryption=server_side_encryption,
            source=source,
            source_hash=source_hash,
            storage_class=storage_class,
            tags=tags,
            tags_all=tags_all,
            website_redirect=website_redirect,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAcl")
    def reset_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAcl", []))

    @jsii.member(jsii_name="resetBucketKeyEnabled")
    def reset_bucket_key_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketKeyEnabled", []))

    @jsii.member(jsii_name="resetCacheControl")
    def reset_cache_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheControl", []))

    @jsii.member(jsii_name="resetContent")
    def reset_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContent", []))

    @jsii.member(jsii_name="resetContentBase64")
    def reset_content_base64(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentBase64", []))

    @jsii.member(jsii_name="resetContentDisposition")
    def reset_content_disposition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentDisposition", []))

    @jsii.member(jsii_name="resetContentEncoding")
    def reset_content_encoding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentEncoding", []))

    @jsii.member(jsii_name="resetContentLanguage")
    def reset_content_language(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentLanguage", []))

    @jsii.member(jsii_name="resetContentType")
    def reset_content_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentType", []))

    @jsii.member(jsii_name="resetEtag")
    def reset_etag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEtag", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetMetadata")
    def reset_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadata", []))

    @jsii.member(jsii_name="resetObjectLockLegalHoldStatus")
    def reset_object_lock_legal_hold_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockLegalHoldStatus", []))

    @jsii.member(jsii_name="resetObjectLockMode")
    def reset_object_lock_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockMode", []))

    @jsii.member(jsii_name="resetObjectLockRetainUntilDate")
    def reset_object_lock_retain_until_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockRetainUntilDate", []))

    @jsii.member(jsii_name="resetServerSideEncryption")
    def reset_server_side_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryption", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetSourceHash")
    def reset_source_hash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceHash", []))

    @jsii.member(jsii_name="resetStorageClass")
    def reset_storage_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageClass", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetWebsiteRedirect")
    def reset_website_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebsiteRedirect", []))

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
    @jsii.member(jsii_name="versionId")
    def version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclInput")
    def acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aclInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketKeyEnabledInput")
    def bucket_key_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "bucketKeyEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheControlInput")
    def cache_control_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheControlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentBase64Input")
    def content_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentBase64Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentDispositionInput")
    def content_disposition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentDispositionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentEncodingInput")
    def content_encoding_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentEncodingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentInput")
    def content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentLanguageInput")
    def content_language_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentLanguageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeInput")
    def content_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etagInput")
    def etag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "etagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "metadataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockLegalHoldStatusInput")
    def object_lock_legal_hold_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockLegalHoldStatusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockModeInput")
    def object_lock_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockRetainUntilDateInput")
    def object_lock_retain_until_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockRetainUntilDateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryptionInput")
    def server_side_encryption_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverSideEncryptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceHashInput")
    def source_hash_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceHashInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClassInput")
    def storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageClassInput"))

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
    @jsii.member(jsii_name="websiteRedirectInput")
    def website_redirect_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "websiteRedirectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acl")
    def acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acl"))

    @acl.setter
    def acl(self, value: builtins.str) -> None:
        jsii.set(self, "acl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketKeyEnabled")
    def bucket_key_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "bucketKeyEnabled"))

    @bucket_key_enabled.setter
    def bucket_key_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "bucketKeyEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheControl")
    def cache_control(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheControl"))

    @cache_control.setter
    def cache_control(self, value: builtins.str) -> None:
        jsii.set(self, "cacheControl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @content.setter
    def content(self, value: builtins.str) -> None:
        jsii.set(self, "content", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentBase64")
    def content_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentBase64"))

    @content_base64.setter
    def content_base64(self, value: builtins.str) -> None:
        jsii.set(self, "contentBase64", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentDisposition")
    def content_disposition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentDisposition"))

    @content_disposition.setter
    def content_disposition(self, value: builtins.str) -> None:
        jsii.set(self, "contentDisposition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentEncoding")
    def content_encoding(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentEncoding"))

    @content_encoding.setter
    def content_encoding(self, value: builtins.str) -> None:
        jsii.set(self, "contentEncoding", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentLanguage")
    def content_language(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentLanguage"))

    @content_language.setter
    def content_language(self, value: builtins.str) -> None:
        jsii.set(self, "contentLanguage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: builtins.str) -> None:
        jsii.set(self, "contentType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @etag.setter
    def etag(self, value: builtins.str) -> None:
        jsii.set(self, "etag", value)

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
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadata")
    def metadata(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "metadata", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockLegalHoldStatus")
    def object_lock_legal_hold_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockLegalHoldStatus"))

    @object_lock_legal_hold_status.setter
    def object_lock_legal_hold_status(self, value: builtins.str) -> None:
        jsii.set(self, "objectLockLegalHoldStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockMode")
    def object_lock_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockMode"))

    @object_lock_mode.setter
    def object_lock_mode(self, value: builtins.str) -> None:
        jsii.set(self, "objectLockMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockRetainUntilDate")
    def object_lock_retain_until_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockRetainUntilDate"))

    @object_lock_retain_until_date.setter
    def object_lock_retain_until_date(self, value: builtins.str) -> None:
        jsii.set(self, "objectLockRetainUntilDate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryption")
    def server_side_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverSideEncryption"))

    @server_side_encryption.setter
    def server_side_encryption(self, value: builtins.str) -> None:
        jsii.set(self, "serverSideEncryption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        jsii.set(self, "source", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceHash")
    def source_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceHash"))

    @source_hash.setter
    def source_hash(self, value: builtins.str) -> None:
        jsii.set(self, "sourceHash", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClass")
    def storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageClass"))

    @storage_class.setter
    def storage_class(self, value: builtins.str) -> None:
        jsii.set(self, "storageClass", value)

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
    @jsii.member(jsii_name="websiteRedirect")
    def website_redirect(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "websiteRedirect"))

    @website_redirect.setter
    def website_redirect(self, value: builtins.str) -> None:
        jsii.set(self, "websiteRedirect", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketObjectConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "key": "key",
        "acl": "acl",
        "bucket_key_enabled": "bucketKeyEnabled",
        "cache_control": "cacheControl",
        "content": "content",
        "content_base64": "contentBase64",
        "content_disposition": "contentDisposition",
        "content_encoding": "contentEncoding",
        "content_language": "contentLanguage",
        "content_type": "contentType",
        "etag": "etag",
        "force_destroy": "forceDestroy",
        "kms_key_id": "kmsKeyId",
        "metadata": "metadata",
        "object_lock_legal_hold_status": "objectLockLegalHoldStatus",
        "object_lock_mode": "objectLockMode",
        "object_lock_retain_until_date": "objectLockRetainUntilDate",
        "server_side_encryption": "serverSideEncryption",
        "source": "source",
        "source_hash": "sourceHash",
        "storage_class": "storageClass",
        "tags": "tags",
        "tags_all": "tagsAll",
        "website_redirect": "websiteRedirect",
    },
)
class S3BucketObjectConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        key: builtins.str,
        acl: typing.Optional[builtins.str] = None,
        bucket_key_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cache_control: typing.Optional[builtins.str] = None,
        content: typing.Optional[builtins.str] = None,
        content_base64: typing.Optional[builtins.str] = None,
        content_disposition: typing.Optional[builtins.str] = None,
        content_encoding: typing.Optional[builtins.str] = None,
        content_language: typing.Optional[builtins.str] = None,
        content_type: typing.Optional[builtins.str] = None,
        etag: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        object_lock_legal_hold_status: typing.Optional[builtins.str] = None,
        object_lock_mode: typing.Optional[builtins.str] = None,
        object_lock_retain_until_date: typing.Optional[builtins.str] = None,
        server_side_encryption: typing.Optional[builtins.str] = None,
        source: typing.Optional[builtins.str] = None,
        source_hash: typing.Optional[builtins.str] = None,
        storage_class: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        website_redirect: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#bucket S3BucketObject#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#key S3BucketObject#key}.
        :param acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#acl S3BucketObject#acl}.
        :param bucket_key_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#bucket_key_enabled S3BucketObject#bucket_key_enabled}.
        :param cache_control: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#cache_control S3BucketObject#cache_control}.
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content S3BucketObject#content}.
        :param content_base64: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_base64 S3BucketObject#content_base64}.
        :param content_disposition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_disposition S3BucketObject#content_disposition}.
        :param content_encoding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_encoding S3BucketObject#content_encoding}.
        :param content_language: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_language S3BucketObject#content_language}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_type S3BucketObject#content_type}.
        :param etag: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#etag S3BucketObject#etag}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#force_destroy S3BucketObject#force_destroy}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#kms_key_id S3BucketObject#kms_key_id}.
        :param metadata: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#metadata S3BucketObject#metadata}.
        :param object_lock_legal_hold_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#object_lock_legal_hold_status S3BucketObject#object_lock_legal_hold_status}.
        :param object_lock_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#object_lock_mode S3BucketObject#object_lock_mode}.
        :param object_lock_retain_until_date: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#object_lock_retain_until_date S3BucketObject#object_lock_retain_until_date}.
        :param server_side_encryption: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#server_side_encryption S3BucketObject#server_side_encryption}.
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#source S3BucketObject#source}.
        :param source_hash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#source_hash S3BucketObject#source_hash}.
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#storage_class S3BucketObject#storage_class}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#tags S3BucketObject#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#tags_all S3BucketObject#tags_all}.
        :param website_redirect: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#website_redirect S3BucketObject#website_redirect}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "key": key,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if acl is not None:
            self._values["acl"] = acl
        if bucket_key_enabled is not None:
            self._values["bucket_key_enabled"] = bucket_key_enabled
        if cache_control is not None:
            self._values["cache_control"] = cache_control
        if content is not None:
            self._values["content"] = content
        if content_base64 is not None:
            self._values["content_base64"] = content_base64
        if content_disposition is not None:
            self._values["content_disposition"] = content_disposition
        if content_encoding is not None:
            self._values["content_encoding"] = content_encoding
        if content_language is not None:
            self._values["content_language"] = content_language
        if content_type is not None:
            self._values["content_type"] = content_type
        if etag is not None:
            self._values["etag"] = etag
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if metadata is not None:
            self._values["metadata"] = metadata
        if object_lock_legal_hold_status is not None:
            self._values["object_lock_legal_hold_status"] = object_lock_legal_hold_status
        if object_lock_mode is not None:
            self._values["object_lock_mode"] = object_lock_mode
        if object_lock_retain_until_date is not None:
            self._values["object_lock_retain_until_date"] = object_lock_retain_until_date
        if server_side_encryption is not None:
            self._values["server_side_encryption"] = server_side_encryption
        if source is not None:
            self._values["source"] = source
        if source_hash is not None:
            self._values["source_hash"] = source_hash
        if storage_class is not None:
            self._values["storage_class"] = storage_class
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if website_redirect is not None:
            self._values["website_redirect"] = website_redirect

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#bucket S3BucketObject#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#key S3BucketObject#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#acl S3BucketObject#acl}.'''
        result = self._values.get("acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_key_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#bucket_key_enabled S3BucketObject#bucket_key_enabled}.'''
        result = self._values.get("bucket_key_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def cache_control(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#cache_control S3BucketObject#cache_control}.'''
        result = self._values.get("cache_control")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content S3BucketObject#content}.'''
        result = self._values.get("content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_base64(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_base64 S3BucketObject#content_base64}.'''
        result = self._values.get("content_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_disposition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_disposition S3BucketObject#content_disposition}.'''
        result = self._values.get("content_disposition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_encoding(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_encoding S3BucketObject#content_encoding}.'''
        result = self._values.get("content_encoding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_language(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_language S3BucketObject#content_language}.'''
        result = self._values.get("content_language")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#content_type S3BucketObject#content_type}.'''
        result = self._values.get("content_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def etag(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#etag S3BucketObject#etag}.'''
        result = self._values.get("etag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#force_destroy S3BucketObject#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#kms_key_id S3BucketObject#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#metadata S3BucketObject#metadata}.'''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def object_lock_legal_hold_status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#object_lock_legal_hold_status S3BucketObject#object_lock_legal_hold_status}.'''
        result = self._values.get("object_lock_legal_hold_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lock_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#object_lock_mode S3BucketObject#object_lock_mode}.'''
        result = self._values.get("object_lock_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lock_retain_until_date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#object_lock_retain_until_date S3BucketObject#object_lock_retain_until_date}.'''
        result = self._values.get("object_lock_retain_until_date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_encryption(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#server_side_encryption S3BucketObject#server_side_encryption}.'''
        result = self._values.get("server_side_encryption")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#source S3BucketObject#source}.'''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_hash(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#source_hash S3BucketObject#source_hash}.'''
        result = self._values.get("source_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#storage_class S3BucketObject#storage_class}.'''
        result = self._values.get("storage_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#tags S3BucketObject#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#tags_all S3BucketObject#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def website_redirect(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_object#website_redirect S3BucketObject#website_redirect}.'''
        result = self._values.get("website_redirect")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketObjectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketObjectLockConfiguration",
    jsii_struct_bases=[],
    name_mapping={"object_lock_enabled": "objectLockEnabled", "rule": "rule"},
)
class S3BucketObjectLockConfiguration:
    def __init__(
        self,
        *,
        object_lock_enabled: builtins.str,
        rule: typing.Optional["S3BucketObjectLockConfigurationRule"] = None,
    ) -> None:
        '''
        :param object_lock_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#object_lock_enabled S3Bucket#object_lock_enabled}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#rule S3Bucket#rule}
        '''
        if isinstance(rule, dict):
            rule = S3BucketObjectLockConfigurationRule(**rule)
        self._values: typing.Dict[str, typing.Any] = {
            "object_lock_enabled": object_lock_enabled,
        }
        if rule is not None:
            self._values["rule"] = rule

    @builtins.property
    def object_lock_enabled(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#object_lock_enabled S3Bucket#object_lock_enabled}.'''
        result = self._values.get("object_lock_enabled")
        assert result is not None, "Required property 'object_lock_enabled' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule(self) -> typing.Optional["S3BucketObjectLockConfigurationRule"]:
        '''rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#rule S3Bucket#rule}
        '''
        result = self._values.get("rule")
        return typing.cast(typing.Optional["S3BucketObjectLockConfigurationRule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketObjectLockConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketObjectLockConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketObjectLockConfigurationOutputReference",
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

    @jsii.member(jsii_name="putRule")
    def put_rule(
        self,
        *,
        default_retention: "S3BucketObjectLockConfigurationRuleDefaultRetention",
    ) -> None:
        '''
        :param default_retention: default_retention block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#default_retention S3Bucket#default_retention}
        '''
        value = S3BucketObjectLockConfigurationRule(
            default_retention=default_retention
        )

        return typing.cast(None, jsii.invoke(self, "putRule", [value]))

    @jsii.member(jsii_name="resetRule")
    def reset_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRule", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rule")
    def rule(self) -> "S3BucketObjectLockConfigurationRuleOutputReference":
        return typing.cast("S3BucketObjectLockConfigurationRuleOutputReference", jsii.get(self, "rule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockEnabledInput")
    def object_lock_enabled_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleInput")
    def rule_input(self) -> typing.Optional["S3BucketObjectLockConfigurationRule"]:
        return typing.cast(typing.Optional["S3BucketObjectLockConfigurationRule"], jsii.get(self, "ruleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockEnabled")
    def object_lock_enabled(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockEnabled"))

    @object_lock_enabled.setter
    def object_lock_enabled(self, value: builtins.str) -> None:
        jsii.set(self, "objectLockEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketObjectLockConfiguration]:
        return typing.cast(typing.Optional[S3BucketObjectLockConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketObjectLockConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketObjectLockConfigurationRule",
    jsii_struct_bases=[],
    name_mapping={"default_retention": "defaultRetention"},
)
class S3BucketObjectLockConfigurationRule:
    def __init__(
        self,
        *,
        default_retention: "S3BucketObjectLockConfigurationRuleDefaultRetention",
    ) -> None:
        '''
        :param default_retention: default_retention block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#default_retention S3Bucket#default_retention}
        '''
        if isinstance(default_retention, dict):
            default_retention = S3BucketObjectLockConfigurationRuleDefaultRetention(**default_retention)
        self._values: typing.Dict[str, typing.Any] = {
            "default_retention": default_retention,
        }

    @builtins.property
    def default_retention(
        self,
    ) -> "S3BucketObjectLockConfigurationRuleDefaultRetention":
        '''default_retention block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#default_retention S3Bucket#default_retention}
        '''
        result = self._values.get("default_retention")
        assert result is not None, "Required property 'default_retention' is missing"
        return typing.cast("S3BucketObjectLockConfigurationRuleDefaultRetention", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketObjectLockConfigurationRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketObjectLockConfigurationRuleDefaultRetention",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "days": "days", "years": "years"},
)
class S3BucketObjectLockConfigurationRuleDefaultRetention:
    def __init__(
        self,
        *,
        mode: builtins.str,
        days: typing.Optional[jsii.Number] = None,
        years: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#mode S3Bucket#mode}.
        :param days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.
        :param years: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#years S3Bucket#years}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mode": mode,
        }
        if days is not None:
            self._values["days"] = days
        if years is not None:
            self._values["years"] = years

    @builtins.property
    def mode(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#mode S3Bucket#mode}.'''
        result = self._values.get("mode")
        assert result is not None, "Required property 'mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.'''
        result = self._values.get("days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def years(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#years S3Bucket#years}.'''
        result = self._values.get("years")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketObjectLockConfigurationRuleDefaultRetention(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketObjectLockConfigurationRuleDefaultRetentionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketObjectLockConfigurationRuleDefaultRetentionOutputReference",
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

    @jsii.member(jsii_name="resetDays")
    def reset_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDays", []))

    @jsii.member(jsii_name="resetYears")
    def reset_years(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetYears", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="daysInput")
    def days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "daysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="yearsInput")
    def years_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "yearsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="days")
    def days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "days"))

    @days.setter
    def days(self, value: jsii.Number) -> None:
        jsii.set(self, "days", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        jsii.set(self, "mode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="years")
    def years(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "years"))

    @years.setter
    def years(self, value: jsii.Number) -> None:
        jsii.set(self, "years", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketObjectLockConfigurationRuleDefaultRetention]:
        return typing.cast(typing.Optional[S3BucketObjectLockConfigurationRuleDefaultRetention], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketObjectLockConfigurationRuleDefaultRetention],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketObjectLockConfigurationRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketObjectLockConfigurationRuleOutputReference",
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

    @jsii.member(jsii_name="putDefaultRetention")
    def put_default_retention(
        self,
        *,
        mode: builtins.str,
        days: typing.Optional[jsii.Number] = None,
        years: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#mode S3Bucket#mode}.
        :param days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#days S3Bucket#days}.
        :param years: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#years S3Bucket#years}.
        '''
        value = S3BucketObjectLockConfigurationRuleDefaultRetention(
            mode=mode, days=days, years=years
        )

        return typing.cast(None, jsii.invoke(self, "putDefaultRetention", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRetention")
    def default_retention(
        self,
    ) -> S3BucketObjectLockConfigurationRuleDefaultRetentionOutputReference:
        return typing.cast(S3BucketObjectLockConfigurationRuleDefaultRetentionOutputReference, jsii.get(self, "defaultRetention"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRetentionInput")
    def default_retention_input(
        self,
    ) -> typing.Optional[S3BucketObjectLockConfigurationRuleDefaultRetention]:
        return typing.cast(typing.Optional[S3BucketObjectLockConfigurationRuleDefaultRetention], jsii.get(self, "defaultRetentionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketObjectLockConfigurationRule]:
        return typing.cast(typing.Optional[S3BucketObjectLockConfigurationRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketObjectLockConfigurationRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketOwnershipControls(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketOwnershipControls",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls aws_s3_bucket_ownership_controls}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        rule: "S3BucketOwnershipControlsRule",
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls aws_s3_bucket_ownership_controls} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls#bucket S3BucketOwnershipControls#bucket}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls#rule S3BucketOwnershipControls#rule}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketOwnershipControlsConfig(
            bucket=bucket,
            rule=rule,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putRule")
    def put_rule(self, *, object_ownership: builtins.str) -> None:
        '''
        :param object_ownership: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls#object_ownership S3BucketOwnershipControls#object_ownership}.
        '''
        value = S3BucketOwnershipControlsRule(object_ownership=object_ownership)

        return typing.cast(None, jsii.invoke(self, "putRule", [value]))

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
    @jsii.member(jsii_name="rule")
    def rule(self) -> "S3BucketOwnershipControlsRuleOutputReference":
        return typing.cast("S3BucketOwnershipControlsRuleOutputReference", jsii.get(self, "rule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleInput")
    def rule_input(self) -> typing.Optional["S3BucketOwnershipControlsRule"]:
        return typing.cast(typing.Optional["S3BucketOwnershipControlsRule"], jsii.get(self, "ruleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketOwnershipControlsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "rule": "rule",
    },
)
class S3BucketOwnershipControlsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        rule: "S3BucketOwnershipControlsRule",
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls#bucket S3BucketOwnershipControls#bucket}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls#rule S3BucketOwnershipControls#rule}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(rule, dict):
            rule = S3BucketOwnershipControlsRule(**rule)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "rule": rule,
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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls#bucket S3BucketOwnershipControls#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule(self) -> "S3BucketOwnershipControlsRule":
        '''rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls#rule S3BucketOwnershipControls#rule}
        '''
        result = self._values.get("rule")
        assert result is not None, "Required property 'rule' is missing"
        return typing.cast("S3BucketOwnershipControlsRule", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketOwnershipControlsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketOwnershipControlsRule",
    jsii_struct_bases=[],
    name_mapping={"object_ownership": "objectOwnership"},
)
class S3BucketOwnershipControlsRule:
    def __init__(self, *, object_ownership: builtins.str) -> None:
        '''
        :param object_ownership: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls#object_ownership S3BucketOwnershipControls#object_ownership}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "object_ownership": object_ownership,
        }

    @builtins.property
    def object_ownership(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_ownership_controls#object_ownership S3BucketOwnershipControls#object_ownership}.'''
        result = self._values.get("object_ownership")
        assert result is not None, "Required property 'object_ownership' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketOwnershipControlsRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketOwnershipControlsRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketOwnershipControlsRuleOutputReference",
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
    @jsii.member(jsii_name="objectOwnershipInput")
    def object_ownership_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectOwnershipInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectOwnership")
    def object_ownership(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectOwnership"))

    @object_ownership.setter
    def object_ownership(self, value: builtins.str) -> None:
        jsii.set(self, "objectOwnership", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketOwnershipControlsRule]:
        return typing.cast(typing.Optional[S3BucketOwnershipControlsRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketOwnershipControlsRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_policy aws_s3_bucket_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        policy: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_policy aws_s3_bucket_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_policy#bucket S3BucketPolicy#bucket}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_policy#policy S3BucketPolicy#policy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketPolicyConfig(
            bucket=bucket,
            policy=policy,
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
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "policy": "policy",
    },
)
class S3BucketPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        policy: builtins.str,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_policy#bucket S3BucketPolicy#bucket}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_policy#policy S3BucketPolicy#policy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "policy": policy,
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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_policy#bucket S3BucketPolicy#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_policy#policy S3BucketPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketPublicAccessBlock(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketPublicAccessBlock",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block aws_s3_bucket_public_access_block}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        block_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restrict_public_buckets: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block aws_s3_bucket_public_access_block} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#bucket S3BucketPublicAccessBlock#bucket}.
        :param block_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#block_public_acls S3BucketPublicAccessBlock#block_public_acls}.
        :param block_public_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#block_public_policy S3BucketPublicAccessBlock#block_public_policy}.
        :param ignore_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#ignore_public_acls S3BucketPublicAccessBlock#ignore_public_acls}.
        :param restrict_public_buckets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#restrict_public_buckets S3BucketPublicAccessBlock#restrict_public_buckets}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketPublicAccessBlockConfig(
            bucket=bucket,
            block_public_acls=block_public_acls,
            block_public_policy=block_public_policy,
            ignore_public_acls=ignore_public_acls,
            restrict_public_buckets=restrict_public_buckets,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetBlockPublicAcls")
    def reset_block_public_acls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPublicAcls", []))

    @jsii.member(jsii_name="resetBlockPublicPolicy")
    def reset_block_public_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPublicPolicy", []))

    @jsii.member(jsii_name="resetIgnorePublicAcls")
    def reset_ignore_public_acls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnorePublicAcls", []))

    @jsii.member(jsii_name="resetRestrictPublicBuckets")
    def reset_restrict_public_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictPublicBuckets", []))

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
    @jsii.member(jsii_name="blockPublicAclsInput")
    def block_public_acls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "blockPublicAclsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicPolicyInput")
    def block_public_policy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "blockPublicPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePublicAclsInput")
    def ignore_public_acls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ignorePublicAclsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictPublicBucketsInput")
    def restrict_public_buckets_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "restrictPublicBucketsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicAcls")
    def block_public_acls(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "blockPublicAcls"))

    @block_public_acls.setter
    def block_public_acls(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "blockPublicAcls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicPolicy")
    def block_public_policy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "blockPublicPolicy"))

    @block_public_policy.setter
    def block_public_policy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "blockPublicPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePublicAcls")
    def ignore_public_acls(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ignorePublicAcls"))

    @ignore_public_acls.setter
    def ignore_public_acls(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ignorePublicAcls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictPublicBuckets")
    def restrict_public_buckets(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "restrictPublicBuckets"))

    @restrict_public_buckets.setter
    def restrict_public_buckets(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "restrictPublicBuckets", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketPublicAccessBlockConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "block_public_acls": "blockPublicAcls",
        "block_public_policy": "blockPublicPolicy",
        "ignore_public_acls": "ignorePublicAcls",
        "restrict_public_buckets": "restrictPublicBuckets",
    },
)
class S3BucketPublicAccessBlockConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        block_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restrict_public_buckets: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#bucket S3BucketPublicAccessBlock#bucket}.
        :param block_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#block_public_acls S3BucketPublicAccessBlock#block_public_acls}.
        :param block_public_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#block_public_policy S3BucketPublicAccessBlock#block_public_policy}.
        :param ignore_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#ignore_public_acls S3BucketPublicAccessBlock#ignore_public_acls}.
        :param restrict_public_buckets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#restrict_public_buckets S3BucketPublicAccessBlock#restrict_public_buckets}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if block_public_acls is not None:
            self._values["block_public_acls"] = block_public_acls
        if block_public_policy is not None:
            self._values["block_public_policy"] = block_public_policy
        if ignore_public_acls is not None:
            self._values["ignore_public_acls"] = ignore_public_acls
        if restrict_public_buckets is not None:
            self._values["restrict_public_buckets"] = restrict_public_buckets

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#bucket S3BucketPublicAccessBlock#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def block_public_acls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#block_public_acls S3BucketPublicAccessBlock#block_public_acls}.'''
        result = self._values.get("block_public_acls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def block_public_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#block_public_policy S3BucketPublicAccessBlock#block_public_policy}.'''
        result = self._values.get("block_public_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ignore_public_acls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#ignore_public_acls S3BucketPublicAccessBlock#ignore_public_acls}.'''
        result = self._values.get("ignore_public_acls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def restrict_public_buckets(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block#restrict_public_buckets S3BucketPublicAccessBlock#restrict_public_buckets}.'''
        result = self._values.get("restrict_public_buckets")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketPublicAccessBlockConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfiguration",
    jsii_struct_bases=[],
    name_mapping={"role": "role", "rules": "rules"},
)
class S3BucketReplicationConfiguration:
    def __init__(
        self,
        *,
        role: builtins.str,
        rules: typing.Sequence["S3BucketReplicationConfigurationRules"],
    ) -> None:
        '''
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#role S3Bucket#role}.
        :param rules: rules block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#rules S3Bucket#rules}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role": role,
            "rules": rules,
        }

    @builtins.property
    def role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#role S3Bucket#role}.'''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rules(self) -> typing.List["S3BucketReplicationConfigurationRules"]:
        '''rules block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#rules S3Bucket#rules}
        '''
        result = self._values.get("rules")
        assert result is not None, "Required property 'rules' is missing"
        return typing.cast(typing.List["S3BucketReplicationConfigurationRules"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationA(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationA",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration aws_s3_bucket_replication_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        role: builtins.str,
        rule: typing.Sequence["S3BucketReplicationConfigurationRule"],
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration aws_s3_bucket_replication_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#bucket S3BucketReplicationConfigurationA#bucket}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#role S3BucketReplicationConfigurationA#role}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#rule S3BucketReplicationConfigurationA#rule}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3BucketReplicationConfigurationAConfig(
            bucket=bucket,
            role=role,
            rule=rule,
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
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleInput")
    def rule_input(
        self,
    ) -> typing.Optional[typing.List["S3BucketReplicationConfigurationRule"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketReplicationConfigurationRule"]], jsii.get(self, "ruleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rule")
    def rule(self) -> typing.List["S3BucketReplicationConfigurationRule"]:
        return typing.cast(typing.List["S3BucketReplicationConfigurationRule"], jsii.get(self, "rule"))

    @rule.setter
    def rule(self, value: typing.List["S3BucketReplicationConfigurationRule"]) -> None:
        jsii.set(self, "rule", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationAConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "role": "role",
        "rule": "rule",
    },
)
class S3BucketReplicationConfigurationAConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        role: builtins.str,
        rule: typing.Sequence["S3BucketReplicationConfigurationRule"],
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#bucket S3BucketReplicationConfigurationA#bucket}.
        :param role: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#role S3BucketReplicationConfigurationA#role}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#rule S3BucketReplicationConfigurationA#rule}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "role": role,
            "rule": rule,
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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#bucket S3BucketReplicationConfigurationA#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#role S3BucketReplicationConfigurationA#role}.'''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule(self) -> typing.List["S3BucketReplicationConfigurationRule"]:
        '''rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#rule S3BucketReplicationConfigurationA#rule}
        '''
        result = self._values.get("rule")
        assert result is not None, "Required property 'rule' is missing"
        return typing.cast(typing.List["S3BucketReplicationConfigurationRule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationAConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationOutputReference",
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
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rulesInput")
    def rules_input(
        self,
    ) -> typing.Optional[typing.List["S3BucketReplicationConfigurationRules"]]:
        return typing.cast(typing.Optional[typing.List["S3BucketReplicationConfigurationRules"]], jsii.get(self, "rulesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rules")
    def rules(self) -> typing.List["S3BucketReplicationConfigurationRules"]:
        return typing.cast(typing.List["S3BucketReplicationConfigurationRules"], jsii.get(self, "rules"))

    @rules.setter
    def rules(
        self,
        value: typing.List["S3BucketReplicationConfigurationRules"],
    ) -> None:
        jsii.set(self, "rules", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketReplicationConfiguration]:
        return typing.cast(typing.Optional[S3BucketReplicationConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRule",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "status": "status",
        "delete_marker_replication": "deleteMarkerReplication",
        "existing_object_replication": "existingObjectReplication",
        "filter": "filter",
        "id": "id",
        "prefix": "prefix",
        "priority": "priority",
        "source_selection_criteria": "sourceSelectionCriteria",
    },
)
class S3BucketReplicationConfigurationRule:
    def __init__(
        self,
        *,
        destination: "S3BucketReplicationConfigurationRuleDestination",
        status: builtins.str,
        delete_marker_replication: typing.Optional["S3BucketReplicationConfigurationRuleDeleteMarkerReplication"] = None,
        existing_object_replication: typing.Optional["S3BucketReplicationConfigurationRuleExistingObjectReplication"] = None,
        filter: typing.Optional["S3BucketReplicationConfigurationRuleFilter"] = None,
        id: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
        source_selection_criteria: typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteria"] = None,
    ) -> None:
        '''
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#destination S3BucketReplicationConfigurationA#destination}
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        :param delete_marker_replication: delete_marker_replication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#delete_marker_replication S3BucketReplicationConfigurationA#delete_marker_replication}
        :param existing_object_replication: existing_object_replication block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#existing_object_replication S3BucketReplicationConfigurationA#existing_object_replication}
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#filter S3BucketReplicationConfigurationA#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#id S3BucketReplicationConfigurationA#id}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#prefix S3BucketReplicationConfigurationA#prefix}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#priority S3BucketReplicationConfigurationA#priority}.
        :param source_selection_criteria: source_selection_criteria block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#source_selection_criteria S3BucketReplicationConfigurationA#source_selection_criteria}
        '''
        if isinstance(destination, dict):
            destination = S3BucketReplicationConfigurationRuleDestination(**destination)
        if isinstance(delete_marker_replication, dict):
            delete_marker_replication = S3BucketReplicationConfigurationRuleDeleteMarkerReplication(**delete_marker_replication)
        if isinstance(existing_object_replication, dict):
            existing_object_replication = S3BucketReplicationConfigurationRuleExistingObjectReplication(**existing_object_replication)
        if isinstance(filter, dict):
            filter = S3BucketReplicationConfigurationRuleFilter(**filter)
        if isinstance(source_selection_criteria, dict):
            source_selection_criteria = S3BucketReplicationConfigurationRuleSourceSelectionCriteria(**source_selection_criteria)
        self._values: typing.Dict[str, typing.Any] = {
            "destination": destination,
            "status": status,
        }
        if delete_marker_replication is not None:
            self._values["delete_marker_replication"] = delete_marker_replication
        if existing_object_replication is not None:
            self._values["existing_object_replication"] = existing_object_replication
        if filter is not None:
            self._values["filter"] = filter
        if id is not None:
            self._values["id"] = id
        if prefix is not None:
            self._values["prefix"] = prefix
        if priority is not None:
            self._values["priority"] = priority
        if source_selection_criteria is not None:
            self._values["source_selection_criteria"] = source_selection_criteria

    @builtins.property
    def destination(self) -> "S3BucketReplicationConfigurationRuleDestination":
        '''destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#destination S3BucketReplicationConfigurationA#destination}
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("S3BucketReplicationConfigurationRuleDestination", result)

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_marker_replication(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleDeleteMarkerReplication"]:
        '''delete_marker_replication block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#delete_marker_replication S3BucketReplicationConfigurationA#delete_marker_replication}
        '''
        result = self._values.get("delete_marker_replication")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleDeleteMarkerReplication"], result)

    @builtins.property
    def existing_object_replication(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleExistingObjectReplication"]:
        '''existing_object_replication block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#existing_object_replication S3BucketReplicationConfigurationA#existing_object_replication}
        '''
        result = self._values.get("existing_object_replication")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleExistingObjectReplication"], result)

    @builtins.property
    def filter(self) -> typing.Optional["S3BucketReplicationConfigurationRuleFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#filter S3BucketReplicationConfigurationA#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleFilter"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#id S3BucketReplicationConfigurationA#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#prefix S3BucketReplicationConfigurationA#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#priority S3BucketReplicationConfigurationA#priority}.'''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def source_selection_criteria(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteria"]:
        '''source_selection_criteria block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#source_selection_criteria S3BucketReplicationConfigurationA#source_selection_criteria}
        '''
        result = self._values.get("source_selection_criteria")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteria"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDeleteMarkerReplication",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class S3BucketReplicationConfigurationRuleDeleteMarkerReplication:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleDeleteMarkerReplication(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleDeleteMarkerReplicationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDeleteMarkerReplicationOutputReference",
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
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDeleteMarkerReplication]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDeleteMarkerReplication], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleDeleteMarkerReplication],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestination",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "access_control_translation": "accessControlTranslation",
        "account": "account",
        "encryption_configuration": "encryptionConfiguration",
        "metrics": "metrics",
        "replication_time": "replicationTime",
        "storage_class": "storageClass",
    },
)
class S3BucketReplicationConfigurationRuleDestination:
    def __init__(
        self,
        *,
        bucket: builtins.str,
        access_control_translation: typing.Optional["S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation"] = None,
        account: typing.Optional[builtins.str] = None,
        encryption_configuration: typing.Optional["S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration"] = None,
        metrics: typing.Optional["S3BucketReplicationConfigurationRuleDestinationMetrics"] = None,
        replication_time: typing.Optional["S3BucketReplicationConfigurationRuleDestinationReplicationTime"] = None,
        storage_class: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#bucket S3BucketReplicationConfigurationA#bucket}.
        :param access_control_translation: access_control_translation block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#access_control_translation S3BucketReplicationConfigurationA#access_control_translation}
        :param account: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#account S3BucketReplicationConfigurationA#account}.
        :param encryption_configuration: encryption_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#encryption_configuration S3BucketReplicationConfigurationA#encryption_configuration}
        :param metrics: metrics block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#metrics S3BucketReplicationConfigurationA#metrics}
        :param replication_time: replication_time block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#replication_time S3BucketReplicationConfigurationA#replication_time}
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#storage_class S3BucketReplicationConfigurationA#storage_class}.
        '''
        if isinstance(access_control_translation, dict):
            access_control_translation = S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation(**access_control_translation)
        if isinstance(encryption_configuration, dict):
            encryption_configuration = S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration(**encryption_configuration)
        if isinstance(metrics, dict):
            metrics = S3BucketReplicationConfigurationRuleDestinationMetrics(**metrics)
        if isinstance(replication_time, dict):
            replication_time = S3BucketReplicationConfigurationRuleDestinationReplicationTime(**replication_time)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }
        if access_control_translation is not None:
            self._values["access_control_translation"] = access_control_translation
        if account is not None:
            self._values["account"] = account
        if encryption_configuration is not None:
            self._values["encryption_configuration"] = encryption_configuration
        if metrics is not None:
            self._values["metrics"] = metrics
        if replication_time is not None:
            self._values["replication_time"] = replication_time
        if storage_class is not None:
            self._values["storage_class"] = storage_class

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#bucket S3BucketReplicationConfigurationA#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_control_translation(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation"]:
        '''access_control_translation block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#access_control_translation S3BucketReplicationConfigurationA#access_control_translation}
        '''
        result = self._values.get("access_control_translation")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation"], result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#account S3BucketReplicationConfigurationA#account}.'''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_configuration(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration"]:
        '''encryption_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#encryption_configuration S3BucketReplicationConfigurationA#encryption_configuration}
        '''
        result = self._values.get("encryption_configuration")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration"], result)

    @builtins.property
    def metrics(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleDestinationMetrics"]:
        '''metrics block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#metrics S3BucketReplicationConfigurationA#metrics}
        '''
        result = self._values.get("metrics")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleDestinationMetrics"], result)

    @builtins.property
    def replication_time(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleDestinationReplicationTime"]:
        '''replication_time block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#replication_time S3BucketReplicationConfigurationA#replication_time}
        '''
        result = self._values.get("replication_time")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleDestinationReplicationTime"], result)

    @builtins.property
    def storage_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#storage_class S3BucketReplicationConfigurationA#storage_class}.'''
        result = self._values.get("storage_class")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation",
    jsii_struct_bases=[],
    name_mapping={"owner": "owner"},
)
class S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation:
    def __init__(self, *, owner: builtins.str) -> None:
        '''
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#owner S3BucketReplicationConfigurationA#owner}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "owner": owner,
        }

    @builtins.property
    def owner(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#owner S3BucketReplicationConfigurationA#owner}.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleDestinationAccessControlTranslationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationAccessControlTranslationOutputReference",
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
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={"replica_kms_key_id": "replicaKmsKeyId"},
)
class S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration:
    def __init__(self, *, replica_kms_key_id: builtins.str) -> None:
        '''
        :param replica_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#replica_kms_key_id S3BucketReplicationConfigurationA#replica_kms_key_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "replica_kms_key_id": replica_kms_key_id,
        }

    @builtins.property
    def replica_kms_key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#replica_kms_key_id S3BucketReplicationConfigurationA#replica_kms_key_id}.'''
        result = self._values.get("replica_kms_key_id")
        assert result is not None, "Required property 'replica_kms_key_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleDestinationEncryptionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationEncryptionConfigurationOutputReference",
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
    @jsii.member(jsii_name="replicaKmsKeyIdInput")
    def replica_kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicaKmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaKmsKeyId")
    def replica_kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicaKmsKeyId"))

    @replica_kms_key_id.setter
    def replica_kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "replicaKmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationMetrics",
    jsii_struct_bases=[],
    name_mapping={"status": "status", "event_threshold": "eventThreshold"},
)
class S3BucketReplicationConfigurationRuleDestinationMetrics:
    def __init__(
        self,
        *,
        status: builtins.str,
        event_threshold: typing.Optional["S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold"] = None,
    ) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        :param event_threshold: event_threshold block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#event_threshold S3BucketReplicationConfigurationA#event_threshold}
        '''
        if isinstance(event_threshold, dict):
            event_threshold = S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold(**event_threshold)
        self._values: typing.Dict[str, typing.Any] = {
            "status": status,
        }
        if event_threshold is not None:
            self._values["event_threshold"] = event_threshold

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def event_threshold(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold"]:
        '''event_threshold block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#event_threshold S3BucketReplicationConfigurationA#event_threshold}
        '''
        result = self._values.get("event_threshold")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleDestinationMetrics(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold",
    jsii_struct_bases=[],
    name_mapping={"minutes": "minutes"},
)
class S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold:
    def __init__(self, *, minutes: jsii.Number) -> None:
        '''
        :param minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#minutes S3BucketReplicationConfigurationA#minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "minutes": minutes,
        }

    @builtins.property
    def minutes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#minutes S3BucketReplicationConfigurationA#minutes}.'''
        result = self._values.get("minutes")
        assert result is not None, "Required property 'minutes' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleDestinationMetricsEventThresholdOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationMetricsEventThresholdOutputReference",
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
    @jsii.member(jsii_name="minutesInput")
    def minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "minutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketReplicationConfigurationRuleDestinationMetricsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationMetricsOutputReference",
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

    @jsii.member(jsii_name="putEventThreshold")
    def put_event_threshold(self, *, minutes: jsii.Number) -> None:
        '''
        :param minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#minutes S3BucketReplicationConfigurationA#minutes}.
        '''
        value = S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold(
            minutes=minutes
        )

        return typing.cast(None, jsii.invoke(self, "putEventThreshold", [value]))

    @jsii.member(jsii_name="resetEventThreshold")
    def reset_event_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventThreshold", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventThreshold")
    def event_threshold(
        self,
    ) -> S3BucketReplicationConfigurationRuleDestinationMetricsEventThresholdOutputReference:
        return typing.cast(S3BucketReplicationConfigurationRuleDestinationMetricsEventThresholdOutputReference, jsii.get(self, "eventThreshold"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventThresholdInput")
    def event_threshold_input(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold], jsii.get(self, "eventThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetrics]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetrics], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetrics],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketReplicationConfigurationRuleDestinationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationOutputReference",
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

    @jsii.member(jsii_name="putAccessControlTranslation")
    def put_access_control_translation(self, *, owner: builtins.str) -> None:
        '''
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#owner S3BucketReplicationConfigurationA#owner}.
        '''
        value = S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation(
            owner=owner
        )

        return typing.cast(None, jsii.invoke(self, "putAccessControlTranslation", [value]))

    @jsii.member(jsii_name="putEncryptionConfiguration")
    def put_encryption_configuration(self, *, replica_kms_key_id: builtins.str) -> None:
        '''
        :param replica_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#replica_kms_key_id S3BucketReplicationConfigurationA#replica_kms_key_id}.
        '''
        value = S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration(
            replica_kms_key_id=replica_kms_key_id
        )

        return typing.cast(None, jsii.invoke(self, "putEncryptionConfiguration", [value]))

    @jsii.member(jsii_name="putMetrics")
    def put_metrics(
        self,
        *,
        status: builtins.str,
        event_threshold: typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold] = None,
    ) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        :param event_threshold: event_threshold block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#event_threshold S3BucketReplicationConfigurationA#event_threshold}
        '''
        value = S3BucketReplicationConfigurationRuleDestinationMetrics(
            status=status, event_threshold=event_threshold
        )

        return typing.cast(None, jsii.invoke(self, "putMetrics", [value]))

    @jsii.member(jsii_name="putReplicationTime")
    def put_replication_time(
        self,
        *,
        status: builtins.str,
        time: "S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime",
    ) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        :param time: time block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#time S3BucketReplicationConfigurationA#time}
        '''
        value = S3BucketReplicationConfigurationRuleDestinationReplicationTime(
            status=status, time=time
        )

        return typing.cast(None, jsii.invoke(self, "putReplicationTime", [value]))

    @jsii.member(jsii_name="resetAccessControlTranslation")
    def reset_access_control_translation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessControlTranslation", []))

    @jsii.member(jsii_name="resetAccount")
    def reset_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccount", []))

    @jsii.member(jsii_name="resetEncryptionConfiguration")
    def reset_encryption_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionConfiguration", []))

    @jsii.member(jsii_name="resetMetrics")
    def reset_metrics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetrics", []))

    @jsii.member(jsii_name="resetReplicationTime")
    def reset_replication_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationTime", []))

    @jsii.member(jsii_name="resetStorageClass")
    def reset_storage_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageClass", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlTranslation")
    def access_control_translation(
        self,
    ) -> S3BucketReplicationConfigurationRuleDestinationAccessControlTranslationOutputReference:
        return typing.cast(S3BucketReplicationConfigurationRuleDestinationAccessControlTranslationOutputReference, jsii.get(self, "accessControlTranslation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfiguration")
    def encryption_configuration(
        self,
    ) -> S3BucketReplicationConfigurationRuleDestinationEncryptionConfigurationOutputReference:
        return typing.cast(S3BucketReplicationConfigurationRuleDestinationEncryptionConfigurationOutputReference, jsii.get(self, "encryptionConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metrics")
    def metrics(
        self,
    ) -> S3BucketReplicationConfigurationRuleDestinationMetricsOutputReference:
        return typing.cast(S3BucketReplicationConfigurationRuleDestinationMetricsOutputReference, jsii.get(self, "metrics"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTime")
    def replication_time(
        self,
    ) -> "S3BucketReplicationConfigurationRuleDestinationReplicationTimeOutputReference":
        return typing.cast("S3BucketReplicationConfigurationRuleDestinationReplicationTimeOutputReference", jsii.get(self, "replicationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlTranslationInput")
    def access_control_translation_input(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation], jsii.get(self, "accessControlTranslationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountInput")
    def account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionConfigurationInput")
    def encryption_configuration_input(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration], jsii.get(self, "encryptionConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricsInput")
    def metrics_input(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetrics]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationMetrics], jsii.get(self, "metricsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTimeInput")
    def replication_time_input(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleDestinationReplicationTime"]:
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleDestinationReplicationTime"], jsii.get(self, "replicationTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClassInput")
    def storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="account")
    def account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "account"))

    @account.setter
    def account(self, value: builtins.str) -> None:
        jsii.set(self, "account", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClass")
    def storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageClass"))

    @storage_class.setter
    def storage_class(self, value: builtins.str) -> None:
        jsii.set(self, "storageClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestination]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestination], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleDestination],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationReplicationTime",
    jsii_struct_bases=[],
    name_mapping={"status": "status", "time": "time"},
)
class S3BucketReplicationConfigurationRuleDestinationReplicationTime:
    def __init__(
        self,
        *,
        status: builtins.str,
        time: "S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime",
    ) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        :param time: time block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#time S3BucketReplicationConfigurationA#time}
        '''
        if isinstance(time, dict):
            time = S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime(**time)
        self._values: typing.Dict[str, typing.Any] = {
            "status": status,
            "time": time,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def time(
        self,
    ) -> "S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime":
        '''time block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#time S3BucketReplicationConfigurationA#time}
        '''
        result = self._values.get("time")
        assert result is not None, "Required property 'time' is missing"
        return typing.cast("S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleDestinationReplicationTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleDestinationReplicationTimeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationReplicationTimeOutputReference",
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

    @jsii.member(jsii_name="putTime")
    def put_time(self, *, minutes: jsii.Number) -> None:
        '''
        :param minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#minutes S3BucketReplicationConfigurationA#minutes}.
        '''
        value = S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime(
            minutes=minutes
        )

        return typing.cast(None, jsii.invoke(self, "putTime", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="time")
    def time(
        self,
    ) -> "S3BucketReplicationConfigurationRuleDestinationReplicationTimeTimeOutputReference":
        return typing.cast("S3BucketReplicationConfigurationRuleDestinationReplicationTimeTimeOutputReference", jsii.get(self, "time"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeInput")
    def time_input(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime"]:
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime"], jsii.get(self, "timeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationReplicationTime]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationReplicationTime], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleDestinationReplicationTime],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime",
    jsii_struct_bases=[],
    name_mapping={"minutes": "minutes"},
)
class S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime:
    def __init__(self, *, minutes: jsii.Number) -> None:
        '''
        :param minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#minutes S3BucketReplicationConfigurationA#minutes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "minutes": minutes,
        }

    @builtins.property
    def minutes(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#minutes S3BucketReplicationConfigurationA#minutes}.'''
        result = self._values.get("minutes")
        assert result is not None, "Required property 'minutes' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleDestinationReplicationTimeTimeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleDestinationReplicationTimeTimeOutputReference",
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
    @jsii.member(jsii_name="minutesInput")
    def minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "minutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleExistingObjectReplication",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class S3BucketReplicationConfigurationRuleExistingObjectReplication:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleExistingObjectReplication(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleExistingObjectReplicationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleExistingObjectReplicationOutputReference",
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
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleExistingObjectReplication]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleExistingObjectReplication], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleExistingObjectReplication],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleFilter",
    jsii_struct_bases=[],
    name_mapping={"and_": "and", "prefix": "prefix", "tag": "tag"},
)
class S3BucketReplicationConfigurationRuleFilter:
    def __init__(
        self,
        *,
        and_: typing.Optional["S3BucketReplicationConfigurationRuleFilterAnd"] = None,
        prefix: typing.Optional[builtins.str] = None,
        tag: typing.Optional["S3BucketReplicationConfigurationRuleFilterTag"] = None,
    ) -> None:
        '''
        :param and_: and block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#and S3BucketReplicationConfigurationA#and}
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#prefix S3BucketReplicationConfigurationA#prefix}.
        :param tag: tag block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#tag S3BucketReplicationConfigurationA#tag}
        '''
        if isinstance(and_, dict):
            and_ = S3BucketReplicationConfigurationRuleFilterAnd(**and_)
        if isinstance(tag, dict):
            tag = S3BucketReplicationConfigurationRuleFilterTag(**tag)
        self._values: typing.Dict[str, typing.Any] = {}
        if and_ is not None:
            self._values["and_"] = and_
        if prefix is not None:
            self._values["prefix"] = prefix
        if tag is not None:
            self._values["tag"] = tag

    @builtins.property
    def and_(self) -> typing.Optional["S3BucketReplicationConfigurationRuleFilterAnd"]:
        '''and block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#and S3BucketReplicationConfigurationA#and}
        '''
        result = self._values.get("and_")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleFilterAnd"], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#prefix S3BucketReplicationConfigurationA#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag(self) -> typing.Optional["S3BucketReplicationConfigurationRuleFilterTag"]:
        '''tag block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#tag S3BucketReplicationConfigurationA#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleFilterTag"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleFilterAnd",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix", "tags": "tags"},
)
class S3BucketReplicationConfigurationRuleFilterAnd:
    def __init__(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#prefix S3BucketReplicationConfigurationA#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#tags S3BucketReplicationConfigurationA#tags}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#prefix S3BucketReplicationConfigurationA#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#tags S3BucketReplicationConfigurationA#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleFilterAnd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleFilterAndOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleFilterAndOutputReference",
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

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleFilterAnd]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleFilterAnd], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleFilterAnd],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketReplicationConfigurationRuleFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleFilterOutputReference",
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

    @jsii.member(jsii_name="putAnd")
    def put_and(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#prefix S3BucketReplicationConfigurationA#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#tags S3BucketReplicationConfigurationA#tags}.
        '''
        value = S3BucketReplicationConfigurationRuleFilterAnd(prefix=prefix, tags=tags)

        return typing.cast(None, jsii.invoke(self, "putAnd", [value]))

    @jsii.member(jsii_name="putTag")
    def put_tag(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#key S3BucketReplicationConfigurationA#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#value S3BucketReplicationConfigurationA#value}.
        '''
        value_ = S3BucketReplicationConfigurationRuleFilterTag(key=key, value=value)

        return typing.cast(None, jsii.invoke(self, "putTag", [value_]))

    @jsii.member(jsii_name="resetAnd")
    def reset_and(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnd", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetTag")
    def reset_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTag", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="and")
    def and_(self) -> S3BucketReplicationConfigurationRuleFilterAndOutputReference:
        return typing.cast(S3BucketReplicationConfigurationRuleFilterAndOutputReference, jsii.get(self, "and"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tag")
    def tag(self) -> "S3BucketReplicationConfigurationRuleFilterTagOutputReference":
        return typing.cast("S3BucketReplicationConfigurationRuleFilterTagOutputReference", jsii.get(self, "tag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="andInput")
    def and_input(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleFilterAnd]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleFilterAnd], jsii.get(self, "andInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagInput")
    def tag_input(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleFilterTag"]:
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleFilterTag"], jsii.get(self, "tagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleFilter]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleFilter],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleFilterTag",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class S3BucketReplicationConfigurationRuleFilterTag:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#key S3BucketReplicationConfigurationA#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#value S3BucketReplicationConfigurationA#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#key S3BucketReplicationConfigurationA#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#value S3BucketReplicationConfigurationA#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleFilterTag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleFilterTagOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleFilterTagOutputReference",
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
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleFilterTag]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleFilterTag], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleFilterTag],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleSourceSelectionCriteria",
    jsii_struct_bases=[],
    name_mapping={
        "replica_modifications": "replicaModifications",
        "sse_kms_encrypted_objects": "sseKmsEncryptedObjects",
    },
)
class S3BucketReplicationConfigurationRuleSourceSelectionCriteria:
    def __init__(
        self,
        *,
        replica_modifications: typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications"] = None,
        sse_kms_encrypted_objects: typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects"] = None,
    ) -> None:
        '''
        :param replica_modifications: replica_modifications block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#replica_modifications S3BucketReplicationConfigurationA#replica_modifications}
        :param sse_kms_encrypted_objects: sse_kms_encrypted_objects block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#sse_kms_encrypted_objects S3BucketReplicationConfigurationA#sse_kms_encrypted_objects}
        '''
        if isinstance(replica_modifications, dict):
            replica_modifications = S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications(**replica_modifications)
        if isinstance(sse_kms_encrypted_objects, dict):
            sse_kms_encrypted_objects = S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects(**sse_kms_encrypted_objects)
        self._values: typing.Dict[str, typing.Any] = {}
        if replica_modifications is not None:
            self._values["replica_modifications"] = replica_modifications
        if sse_kms_encrypted_objects is not None:
            self._values["sse_kms_encrypted_objects"] = sse_kms_encrypted_objects

    @builtins.property
    def replica_modifications(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications"]:
        '''replica_modifications block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#replica_modifications S3BucketReplicationConfigurationA#replica_modifications}
        '''
        result = self._values.get("replica_modifications")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications"], result)

    @builtins.property
    def sse_kms_encrypted_objects(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects"]:
        '''sse_kms_encrypted_objects block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#sse_kms_encrypted_objects S3BucketReplicationConfigurationA#sse_kms_encrypted_objects}
        '''
        result = self._values.get("sse_kms_encrypted_objects")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleSourceSelectionCriteria(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleSourceSelectionCriteriaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleSourceSelectionCriteriaOutputReference",
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

    @jsii.member(jsii_name="putReplicaModifications")
    def put_replica_modifications(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        '''
        value = S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications(
            status=status
        )

        return typing.cast(None, jsii.invoke(self, "putReplicaModifications", [value]))

    @jsii.member(jsii_name="putSseKmsEncryptedObjects")
    def put_sse_kms_encrypted_objects(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        '''
        value = S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects(
            status=status
        )

        return typing.cast(None, jsii.invoke(self, "putSseKmsEncryptedObjects", [value]))

    @jsii.member(jsii_name="resetReplicaModifications")
    def reset_replica_modifications(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicaModifications", []))

    @jsii.member(jsii_name="resetSseKmsEncryptedObjects")
    def reset_sse_kms_encrypted_objects(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSseKmsEncryptedObjects", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaModifications")
    def replica_modifications(
        self,
    ) -> "S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModificationsOutputReference":
        return typing.cast("S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModificationsOutputReference", jsii.get(self, "replicaModifications"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseKmsEncryptedObjects")
    def sse_kms_encrypted_objects(
        self,
    ) -> "S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference":
        return typing.cast("S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference", jsii.get(self, "sseKmsEncryptedObjects"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaModificationsInput")
    def replica_modifications_input(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications"]:
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications"], jsii.get(self, "replicaModificationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseKmsEncryptedObjectsInput")
    def sse_kms_encrypted_objects_input(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects"]:
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects"], jsii.get(self, "sseKmsEncryptedObjectsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleSourceSelectionCriteria]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleSourceSelectionCriteria], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleSourceSelectionCriteria],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModificationsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModificationsOutputReference",
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
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects",
    jsii_struct_bases=[],
    name_mapping={"status": "status"},
)
class S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects:
    def __init__(self, *, status: builtins.str) -> None:
        '''
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "status": status,
        }

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket_replication_configuration#status S3BucketReplicationConfigurationA#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference",
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
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRules",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "status": "status",
        "delete_marker_replication_status": "deleteMarkerReplicationStatus",
        "filter": "filter",
        "id": "id",
        "prefix": "prefix",
        "priority": "priority",
        "source_selection_criteria": "sourceSelectionCriteria",
    },
)
class S3BucketReplicationConfigurationRules:
    def __init__(
        self,
        *,
        destination: "S3BucketReplicationConfigurationRulesDestination",
        status: builtins.str,
        delete_marker_replication_status: typing.Optional[builtins.str] = None,
        filter: typing.Optional["S3BucketReplicationConfigurationRulesFilter"] = None,
        id: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
        source_selection_criteria: typing.Optional["S3BucketReplicationConfigurationRulesSourceSelectionCriteria"] = None,
    ) -> None:
        '''
        :param destination: destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#destination S3Bucket#destination}
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#status S3Bucket#status}.
        :param delete_marker_replication_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#delete_marker_replication_status S3Bucket#delete_marker_replication_status}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#filter S3Bucket#filter}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#id S3Bucket#id}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#prefix S3Bucket#prefix}.
        :param priority: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#priority S3Bucket#priority}.
        :param source_selection_criteria: source_selection_criteria block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#source_selection_criteria S3Bucket#source_selection_criteria}
        '''
        if isinstance(destination, dict):
            destination = S3BucketReplicationConfigurationRulesDestination(**destination)
        if isinstance(filter, dict):
            filter = S3BucketReplicationConfigurationRulesFilter(**filter)
        if isinstance(source_selection_criteria, dict):
            source_selection_criteria = S3BucketReplicationConfigurationRulesSourceSelectionCriteria(**source_selection_criteria)
        self._values: typing.Dict[str, typing.Any] = {
            "destination": destination,
            "status": status,
        }
        if delete_marker_replication_status is not None:
            self._values["delete_marker_replication_status"] = delete_marker_replication_status
        if filter is not None:
            self._values["filter"] = filter
        if id is not None:
            self._values["id"] = id
        if prefix is not None:
            self._values["prefix"] = prefix
        if priority is not None:
            self._values["priority"] = priority
        if source_selection_criteria is not None:
            self._values["source_selection_criteria"] = source_selection_criteria

    @builtins.property
    def destination(self) -> "S3BucketReplicationConfigurationRulesDestination":
        '''destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#destination S3Bucket#destination}
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("S3BucketReplicationConfigurationRulesDestination", result)

    @builtins.property
    def status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#status S3Bucket#status}.'''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_marker_replication_status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#delete_marker_replication_status S3Bucket#delete_marker_replication_status}.'''
        result = self._values.get("delete_marker_replication_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filter(self) -> typing.Optional["S3BucketReplicationConfigurationRulesFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#filter S3Bucket#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRulesFilter"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#id S3Bucket#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#prefix S3Bucket#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#priority S3Bucket#priority}.'''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def source_selection_criteria(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRulesSourceSelectionCriteria"]:
        '''source_selection_criteria block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#source_selection_criteria S3Bucket#source_selection_criteria}
        '''
        result = self._values.get("source_selection_criteria")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRulesSourceSelectionCriteria"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesDestination",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "access_control_translation": "accessControlTranslation",
        "account_id": "accountId",
        "metrics": "metrics",
        "replica_kms_key_id": "replicaKmsKeyId",
        "replication_time": "replicationTime",
        "storage_class": "storageClass",
    },
)
class S3BucketReplicationConfigurationRulesDestination:
    def __init__(
        self,
        *,
        bucket: builtins.str,
        access_control_translation: typing.Optional["S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation"] = None,
        account_id: typing.Optional[builtins.str] = None,
        metrics: typing.Optional["S3BucketReplicationConfigurationRulesDestinationMetrics"] = None,
        replica_kms_key_id: typing.Optional[builtins.str] = None,
        replication_time: typing.Optional["S3BucketReplicationConfigurationRulesDestinationReplicationTime"] = None,
        storage_class: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket S3Bucket#bucket}.
        :param access_control_translation: access_control_translation block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#access_control_translation S3Bucket#access_control_translation}
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#account_id S3Bucket#account_id}.
        :param metrics: metrics block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#metrics S3Bucket#metrics}
        :param replica_kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#replica_kms_key_id S3Bucket#replica_kms_key_id}.
        :param replication_time: replication_time block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#replication_time S3Bucket#replication_time}
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#storage_class S3Bucket#storage_class}.
        '''
        if isinstance(access_control_translation, dict):
            access_control_translation = S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation(**access_control_translation)
        if isinstance(metrics, dict):
            metrics = S3BucketReplicationConfigurationRulesDestinationMetrics(**metrics)
        if isinstance(replication_time, dict):
            replication_time = S3BucketReplicationConfigurationRulesDestinationReplicationTime(**replication_time)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }
        if access_control_translation is not None:
            self._values["access_control_translation"] = access_control_translation
        if account_id is not None:
            self._values["account_id"] = account_id
        if metrics is not None:
            self._values["metrics"] = metrics
        if replica_kms_key_id is not None:
            self._values["replica_kms_key_id"] = replica_kms_key_id
        if replication_time is not None:
            self._values["replication_time"] = replication_time
        if storage_class is not None:
            self._values["storage_class"] = storage_class

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket S3Bucket#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_control_translation(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation"]:
        '''access_control_translation block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#access_control_translation S3Bucket#access_control_translation}
        '''
        result = self._values.get("access_control_translation")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation"], result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#account_id S3Bucket#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metrics(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRulesDestinationMetrics"]:
        '''metrics block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#metrics S3Bucket#metrics}
        '''
        result = self._values.get("metrics")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRulesDestinationMetrics"], result)

    @builtins.property
    def replica_kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#replica_kms_key_id S3Bucket#replica_kms_key_id}.'''
        result = self._values.get("replica_kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_time(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRulesDestinationReplicationTime"]:
        '''replication_time block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#replication_time S3Bucket#replication_time}
        '''
        result = self._values.get("replication_time")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRulesDestinationReplicationTime"], result)

    @builtins.property
    def storage_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#storage_class S3Bucket#storage_class}.'''
        result = self._values.get("storage_class")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRulesDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation",
    jsii_struct_bases=[],
    name_mapping={"owner": "owner"},
)
class S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation:
    def __init__(self, *, owner: builtins.str) -> None:
        '''
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#owner S3Bucket#owner}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "owner": owner,
        }

    @builtins.property
    def owner(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#owner S3Bucket#owner}.'''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRulesDestinationAccessControlTranslationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesDestinationAccessControlTranslationOutputReference",
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
    @jsii.member(jsii_name="ownerInput")
    def owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owner"))

    @owner.setter
    def owner(self, value: builtins.str) -> None:
        jsii.set(self, "owner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesDestinationMetrics",
    jsii_struct_bases=[],
    name_mapping={"minutes": "minutes", "status": "status"},
)
class S3BucketReplicationConfigurationRulesDestinationMetrics:
    def __init__(
        self,
        *,
        minutes: typing.Optional[jsii.Number] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#minutes S3Bucket#minutes}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#status S3Bucket#status}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if minutes is not None:
            self._values["minutes"] = minutes
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#minutes S3Bucket#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#status S3Bucket#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRulesDestinationMetrics(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRulesDestinationMetricsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesDestinationMetricsOutputReference",
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

    @jsii.member(jsii_name="resetMinutes")
    def reset_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinutes", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minutesInput")
    def minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "minutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRulesDestinationMetrics]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRulesDestinationMetrics], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRulesDestinationMetrics],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketReplicationConfigurationRulesDestinationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesDestinationOutputReference",
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

    @jsii.member(jsii_name="putAccessControlTranslation")
    def put_access_control_translation(self, *, owner: builtins.str) -> None:
        '''
        :param owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#owner S3Bucket#owner}.
        '''
        value = S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation(
            owner=owner
        )

        return typing.cast(None, jsii.invoke(self, "putAccessControlTranslation", [value]))

    @jsii.member(jsii_name="putMetrics")
    def put_metrics(
        self,
        *,
        minutes: typing.Optional[jsii.Number] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#minutes S3Bucket#minutes}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#status S3Bucket#status}.
        '''
        value = S3BucketReplicationConfigurationRulesDestinationMetrics(
            minutes=minutes, status=status
        )

        return typing.cast(None, jsii.invoke(self, "putMetrics", [value]))

    @jsii.member(jsii_name="putReplicationTime")
    def put_replication_time(
        self,
        *,
        minutes: typing.Optional[jsii.Number] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#minutes S3Bucket#minutes}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#status S3Bucket#status}.
        '''
        value = S3BucketReplicationConfigurationRulesDestinationReplicationTime(
            minutes=minutes, status=status
        )

        return typing.cast(None, jsii.invoke(self, "putReplicationTime", [value]))

    @jsii.member(jsii_name="resetAccessControlTranslation")
    def reset_access_control_translation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessControlTranslation", []))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetMetrics")
    def reset_metrics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetrics", []))

    @jsii.member(jsii_name="resetReplicaKmsKeyId")
    def reset_replica_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicaKmsKeyId", []))

    @jsii.member(jsii_name="resetReplicationTime")
    def reset_replication_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationTime", []))

    @jsii.member(jsii_name="resetStorageClass")
    def reset_storage_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageClass", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlTranslation")
    def access_control_translation(
        self,
    ) -> S3BucketReplicationConfigurationRulesDestinationAccessControlTranslationOutputReference:
        return typing.cast(S3BucketReplicationConfigurationRulesDestinationAccessControlTranslationOutputReference, jsii.get(self, "accessControlTranslation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metrics")
    def metrics(
        self,
    ) -> S3BucketReplicationConfigurationRulesDestinationMetricsOutputReference:
        return typing.cast(S3BucketReplicationConfigurationRulesDestinationMetricsOutputReference, jsii.get(self, "metrics"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTime")
    def replication_time(
        self,
    ) -> "S3BucketReplicationConfigurationRulesDestinationReplicationTimeOutputReference":
        return typing.cast("S3BucketReplicationConfigurationRulesDestinationReplicationTimeOutputReference", jsii.get(self, "replicationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlTranslationInput")
    def access_control_translation_input(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation], jsii.get(self, "accessControlTranslationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricsInput")
    def metrics_input(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRulesDestinationMetrics]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRulesDestinationMetrics], jsii.get(self, "metricsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaKmsKeyIdInput")
    def replica_kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicaKmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicationTimeInput")
    def replication_time_input(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRulesDestinationReplicationTime"]:
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRulesDestinationReplicationTime"], jsii.get(self, "replicationTimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClassInput")
    def storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaKmsKeyId")
    def replica_kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicaKmsKeyId"))

    @replica_kms_key_id.setter
    def replica_kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "replicaKmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClass")
    def storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageClass"))

    @storage_class.setter
    def storage_class(self, value: builtins.str) -> None:
        jsii.set(self, "storageClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRulesDestination]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRulesDestination], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRulesDestination],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesDestinationReplicationTime",
    jsii_struct_bases=[],
    name_mapping={"minutes": "minutes", "status": "status"},
)
class S3BucketReplicationConfigurationRulesDestinationReplicationTime:
    def __init__(
        self,
        *,
        minutes: typing.Optional[jsii.Number] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param minutes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#minutes S3Bucket#minutes}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#status S3Bucket#status}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if minutes is not None:
            self._values["minutes"] = minutes
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def minutes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#minutes S3Bucket#minutes}.'''
        result = self._values.get("minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#status S3Bucket#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRulesDestinationReplicationTime(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRulesDestinationReplicationTimeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesDestinationReplicationTimeOutputReference",
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

    @jsii.member(jsii_name="resetMinutes")
    def reset_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinutes", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minutesInput")
    def minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minutesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minutes")
    def minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minutes"))

    @minutes.setter
    def minutes(self, value: jsii.Number) -> None:
        jsii.set(self, "minutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRulesDestinationReplicationTime]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRulesDestinationReplicationTime], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRulesDestinationReplicationTime],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesFilter",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix", "tags": "tags"},
)
class S3BucketReplicationConfigurationRulesFilter:
    def __init__(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#prefix S3Bucket#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags S3Bucket#tags}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#prefix S3Bucket#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#tags S3Bucket#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRulesFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRulesFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesFilterOutputReference",
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

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRulesFilter]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRulesFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRulesFilter],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesSourceSelectionCriteria",
    jsii_struct_bases=[],
    name_mapping={"sse_kms_encrypted_objects": "sseKmsEncryptedObjects"},
)
class S3BucketReplicationConfigurationRulesSourceSelectionCriteria:
    def __init__(
        self,
        *,
        sse_kms_encrypted_objects: typing.Optional["S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects"] = None,
    ) -> None:
        '''
        :param sse_kms_encrypted_objects: sse_kms_encrypted_objects block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#sse_kms_encrypted_objects S3Bucket#sse_kms_encrypted_objects}
        '''
        if isinstance(sse_kms_encrypted_objects, dict):
            sse_kms_encrypted_objects = S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects(**sse_kms_encrypted_objects)
        self._values: typing.Dict[str, typing.Any] = {}
        if sse_kms_encrypted_objects is not None:
            self._values["sse_kms_encrypted_objects"] = sse_kms_encrypted_objects

    @builtins.property
    def sse_kms_encrypted_objects(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects"]:
        '''sse_kms_encrypted_objects block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#sse_kms_encrypted_objects S3Bucket#sse_kms_encrypted_objects}
        '''
        result = self._values.get("sse_kms_encrypted_objects")
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRulesSourceSelectionCriteria(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRulesSourceSelectionCriteriaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesSourceSelectionCriteriaOutputReference",
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

    @jsii.member(jsii_name="putSseKmsEncryptedObjects")
    def put_sse_kms_encrypted_objects(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#enabled S3Bucket#enabled}.
        '''
        value = S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects(
            enabled=enabled
        )

        return typing.cast(None, jsii.invoke(self, "putSseKmsEncryptedObjects", [value]))

    @jsii.member(jsii_name="resetSseKmsEncryptedObjects")
    def reset_sse_kms_encrypted_objects(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSseKmsEncryptedObjects", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseKmsEncryptedObjects")
    def sse_kms_encrypted_objects(
        self,
    ) -> "S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference":
        return typing.cast("S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference", jsii.get(self, "sseKmsEncryptedObjects"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseKmsEncryptedObjectsInput")
    def sse_kms_encrypted_objects_input(
        self,
    ) -> typing.Optional["S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects"]:
        return typing.cast(typing.Optional["S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects"], jsii.get(self, "sseKmsEncryptedObjectsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketReplicationConfigurationRulesSourceSelectionCriteria]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRulesSourceSelectionCriteria], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRulesSourceSelectionCriteria],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled"},
)
class S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#enabled S3Bucket#enabled}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
        }

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#enabled S3Bucket#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference",
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
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

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
    ) -> typing.Optional[S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects]:
        return typing.cast(typing.Optional[S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketServerSideEncryptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={"rule": "rule"},
)
class S3BucketServerSideEncryptionConfiguration:
    def __init__(
        self,
        *,
        rule: "S3BucketServerSideEncryptionConfigurationRule",
    ) -> None:
        '''
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#rule S3Bucket#rule}
        '''
        if isinstance(rule, dict):
            rule = S3BucketServerSideEncryptionConfigurationRule(**rule)
        self._values: typing.Dict[str, typing.Any] = {
            "rule": rule,
        }

    @builtins.property
    def rule(self) -> "S3BucketServerSideEncryptionConfigurationRule":
        '''rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#rule S3Bucket#rule}
        '''
        result = self._values.get("rule")
        assert result is not None, "Required property 'rule' is missing"
        return typing.cast("S3BucketServerSideEncryptionConfigurationRule", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketServerSideEncryptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketServerSideEncryptionConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketServerSideEncryptionConfigurationOutputReference",
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

    @jsii.member(jsii_name="putRule")
    def put_rule(
        self,
        *,
        apply_server_side_encryption_by_default: "S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault",
        bucket_key_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param apply_server_side_encryption_by_default: apply_server_side_encryption_by_default block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#apply_server_side_encryption_by_default S3Bucket#apply_server_side_encryption_by_default}
        :param bucket_key_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket_key_enabled S3Bucket#bucket_key_enabled}.
        '''
        value = S3BucketServerSideEncryptionConfigurationRule(
            apply_server_side_encryption_by_default=apply_server_side_encryption_by_default,
            bucket_key_enabled=bucket_key_enabled,
        )

        return typing.cast(None, jsii.invoke(self, "putRule", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rule")
    def rule(self) -> "S3BucketServerSideEncryptionConfigurationRuleOutputReference":
        return typing.cast("S3BucketServerSideEncryptionConfigurationRuleOutputReference", jsii.get(self, "rule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleInput")
    def rule_input(
        self,
    ) -> typing.Optional["S3BucketServerSideEncryptionConfigurationRule"]:
        return typing.cast(typing.Optional["S3BucketServerSideEncryptionConfigurationRule"], jsii.get(self, "ruleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketServerSideEncryptionConfiguration]:
        return typing.cast(typing.Optional[S3BucketServerSideEncryptionConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketServerSideEncryptionConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketServerSideEncryptionConfigurationRule",
    jsii_struct_bases=[],
    name_mapping={
        "apply_server_side_encryption_by_default": "applyServerSideEncryptionByDefault",
        "bucket_key_enabled": "bucketKeyEnabled",
    },
)
class S3BucketServerSideEncryptionConfigurationRule:
    def __init__(
        self,
        *,
        apply_server_side_encryption_by_default: "S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault",
        bucket_key_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param apply_server_side_encryption_by_default: apply_server_side_encryption_by_default block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#apply_server_side_encryption_by_default S3Bucket#apply_server_side_encryption_by_default}
        :param bucket_key_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket_key_enabled S3Bucket#bucket_key_enabled}.
        '''
        if isinstance(apply_server_side_encryption_by_default, dict):
            apply_server_side_encryption_by_default = S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault(**apply_server_side_encryption_by_default)
        self._values: typing.Dict[str, typing.Any] = {
            "apply_server_side_encryption_by_default": apply_server_side_encryption_by_default,
        }
        if bucket_key_enabled is not None:
            self._values["bucket_key_enabled"] = bucket_key_enabled

    @builtins.property
    def apply_server_side_encryption_by_default(
        self,
    ) -> "S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault":
        '''apply_server_side_encryption_by_default block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#apply_server_side_encryption_by_default S3Bucket#apply_server_side_encryption_by_default}
        '''
        result = self._values.get("apply_server_side_encryption_by_default")
        assert result is not None, "Required property 'apply_server_side_encryption_by_default' is missing"
        return typing.cast("S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault", result)

    @builtins.property
    def bucket_key_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#bucket_key_enabled S3Bucket#bucket_key_enabled}.'''
        result = self._values.get("bucket_key_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketServerSideEncryptionConfigurationRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault",
    jsii_struct_bases=[],
    name_mapping={
        "sse_algorithm": "sseAlgorithm",
        "kms_master_key_id": "kmsMasterKeyId",
    },
)
class S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault:
    def __init__(
        self,
        *,
        sse_algorithm: builtins.str,
        kms_master_key_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param sse_algorithm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#sse_algorithm S3Bucket#sse_algorithm}.
        :param kms_master_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#kms_master_key_id S3Bucket#kms_master_key_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "sse_algorithm": sse_algorithm,
        }
        if kms_master_key_id is not None:
            self._values["kms_master_key_id"] = kms_master_key_id

    @builtins.property
    def sse_algorithm(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#sse_algorithm S3Bucket#sse_algorithm}.'''
        result = self._values.get("sse_algorithm")
        assert result is not None, "Required property 'sse_algorithm' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_master_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#kms_master_key_id S3Bucket#kms_master_key_id}.'''
        result = self._values.get("kms_master_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultOutputReference",
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

    @jsii.member(jsii_name="resetKmsMasterKeyId")
    def reset_kms_master_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsMasterKeyId", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsMasterKeyIdInput")
    def kms_master_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsMasterKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseAlgorithmInput")
    def sse_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sseAlgorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsMasterKeyId")
    def kms_master_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsMasterKeyId"))

    @kms_master_key_id.setter
    def kms_master_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsMasterKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sseAlgorithm")
    def sse_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sseAlgorithm"))

    @sse_algorithm.setter
    def sse_algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "sseAlgorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault]:
        return typing.cast(typing.Optional[S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3BucketServerSideEncryptionConfigurationRuleOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketServerSideEncryptionConfigurationRuleOutputReference",
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

    @jsii.member(jsii_name="putApplyServerSideEncryptionByDefault")
    def put_apply_server_side_encryption_by_default(
        self,
        *,
        sse_algorithm: builtins.str,
        kms_master_key_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param sse_algorithm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#sse_algorithm S3Bucket#sse_algorithm}.
        :param kms_master_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#kms_master_key_id S3Bucket#kms_master_key_id}.
        '''
        value = S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault(
            sse_algorithm=sse_algorithm, kms_master_key_id=kms_master_key_id
        )

        return typing.cast(None, jsii.invoke(self, "putApplyServerSideEncryptionByDefault", [value]))

    @jsii.member(jsii_name="resetBucketKeyEnabled")
    def reset_bucket_key_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketKeyEnabled", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyServerSideEncryptionByDefault")
    def apply_server_side_encryption_by_default(
        self,
    ) -> S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultOutputReference:
        return typing.cast(S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultOutputReference, jsii.get(self, "applyServerSideEncryptionByDefault"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applyServerSideEncryptionByDefaultInput")
    def apply_server_side_encryption_by_default_input(
        self,
    ) -> typing.Optional[S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault]:
        return typing.cast(typing.Optional[S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault], jsii.get(self, "applyServerSideEncryptionByDefaultInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketKeyEnabledInput")
    def bucket_key_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "bucketKeyEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketKeyEnabled")
    def bucket_key_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "bucketKeyEnabled"))

    @bucket_key_enabled.setter
    def bucket_key_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "bucketKeyEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3BucketServerSideEncryptionConfigurationRule]:
        return typing.cast(typing.Optional[S3BucketServerSideEncryptionConfigurationRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3BucketServerSideEncryptionConfigurationRule],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketVersioning",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "mfa_delete": "mfaDelete"},
)
class S3BucketVersioning:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        mfa_delete: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#enabled S3Bucket#enabled}.
        :param mfa_delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#mfa_delete S3Bucket#mfa_delete}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if mfa_delete is not None:
            self._values["mfa_delete"] = mfa_delete

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#enabled S3Bucket#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def mfa_delete(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#mfa_delete S3Bucket#mfa_delete}.'''
        result = self._values.get("mfa_delete")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketVersioning(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketVersioningOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketVersioningOutputReference",
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

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetMfaDelete")
    def reset_mfa_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMfaDelete", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mfaDeleteInput")
    def mfa_delete_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "mfaDeleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mfaDelete")
    def mfa_delete(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "mfaDelete"))

    @mfa_delete.setter
    def mfa_delete(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "mfaDelete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketVersioning]:
        return typing.cast(typing.Optional[S3BucketVersioning], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[S3BucketVersioning]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3BucketWebsite",
    jsii_struct_bases=[],
    name_mapping={
        "error_document": "errorDocument",
        "index_document": "indexDocument",
        "redirect_all_requests_to": "redirectAllRequestsTo",
        "routing_rules": "routingRules",
    },
)
class S3BucketWebsite:
    def __init__(
        self,
        *,
        error_document: typing.Optional[builtins.str] = None,
        index_document: typing.Optional[builtins.str] = None,
        redirect_all_requests_to: typing.Optional[builtins.str] = None,
        routing_rules: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param error_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#error_document S3Bucket#error_document}.
        :param index_document: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#index_document S3Bucket#index_document}.
        :param redirect_all_requests_to: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#redirect_all_requests_to S3Bucket#redirect_all_requests_to}.
        :param routing_rules: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#routing_rules S3Bucket#routing_rules}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if error_document is not None:
            self._values["error_document"] = error_document
        if index_document is not None:
            self._values["index_document"] = index_document
        if redirect_all_requests_to is not None:
            self._values["redirect_all_requests_to"] = redirect_all_requests_to
        if routing_rules is not None:
            self._values["routing_rules"] = routing_rules

    @builtins.property
    def error_document(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#error_document S3Bucket#error_document}.'''
        result = self._values.get("error_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def index_document(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#index_document S3Bucket#index_document}.'''
        result = self._values.get("index_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redirect_all_requests_to(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#redirect_all_requests_to S3Bucket#redirect_all_requests_to}.'''
        result = self._values.get("redirect_all_requests_to")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def routing_rules(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_bucket#routing_rules S3Bucket#routing_rules}.'''
        result = self._values.get("routing_rules")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketWebsite(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketWebsiteOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3BucketWebsiteOutputReference",
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

    @jsii.member(jsii_name="resetErrorDocument")
    def reset_error_document(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetErrorDocument", []))

    @jsii.member(jsii_name="resetIndexDocument")
    def reset_index_document(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexDocument", []))

    @jsii.member(jsii_name="resetRedirectAllRequestsTo")
    def reset_redirect_all_requests_to(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirectAllRequestsTo", []))

    @jsii.member(jsii_name="resetRoutingRules")
    def reset_routing_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutingRules", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorDocumentInput")
    def error_document_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "errorDocumentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="indexDocumentInput")
    def index_document_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexDocumentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redirectAllRequestsToInput")
    def redirect_all_requests_to_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redirectAllRequestsToInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingRulesInput")
    def routing_rules_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routingRulesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorDocument")
    def error_document(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorDocument"))

    @error_document.setter
    def error_document(self, value: builtins.str) -> None:
        jsii.set(self, "errorDocument", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="indexDocument")
    def index_document(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexDocument"))

    @index_document.setter
    def index_document(self, value: builtins.str) -> None:
        jsii.set(self, "indexDocument", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redirectAllRequestsTo")
    def redirect_all_requests_to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redirectAllRequestsTo"))

    @redirect_all_requests_to.setter
    def redirect_all_requests_to(self, value: builtins.str) -> None:
        jsii.set(self, "redirectAllRequestsTo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routingRules")
    def routing_rules(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routingRules"))

    @routing_rules.setter
    def routing_rules(self, value: builtins.str) -> None:
        jsii.set(self, "routingRules", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3BucketWebsite]:
        return typing.cast(typing.Optional[S3BucketWebsite], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[S3BucketWebsite]) -> None:
        jsii.set(self, "internalValue", value)


class S3ControlAccessPointPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlAccessPointPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3control_access_point_policy aws_s3control_access_point_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_point_arn: builtins.str,
        policy: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3control_access_point_policy aws_s3control_access_point_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_point_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_access_point_policy#access_point_arn S3ControlAccessPointPolicy#access_point_arn}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_access_point_policy#policy S3ControlAccessPointPolicy#policy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3ControlAccessPointPolicyConfig(
            access_point_arn=access_point_arn,
            policy=policy,
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
    @jsii.member(jsii_name="hasPublicAccessPolicy")
    def has_public_access_policy(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "hasPublicAccessPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointArnInput")
    def access_point_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessPointArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessPointArn")
    def access_point_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessPointArn"))

    @access_point_arn.setter
    def access_point_arn(self, value: builtins.str) -> None:
        jsii.set(self, "accessPointArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlAccessPointPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "access_point_arn": "accessPointArn",
        "policy": "policy",
    },
)
class S3ControlAccessPointPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        access_point_arn: builtins.str,
        policy: builtins.str,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param access_point_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_access_point_policy#access_point_arn S3ControlAccessPointPolicy#access_point_arn}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_access_point_policy#policy S3ControlAccessPointPolicy#policy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "access_point_arn": access_point_arn,
            "policy": policy,
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
    def access_point_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_access_point_policy#access_point_arn S3ControlAccessPointPolicy#access_point_arn}.'''
        result = self._values.get("access_point_arn")
        assert result is not None, "Required property 'access_point_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_access_point_policy#policy S3ControlAccessPointPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlAccessPointPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlBucket(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucket",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket aws_s3control_bucket}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        outpost_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket aws_s3control_bucket} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#bucket S3ControlBucket#bucket}.
        :param outpost_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#outpost_id S3ControlBucket#outpost_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#tags S3ControlBucket#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#tags_all S3ControlBucket#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3ControlBucketConfig(
            bucket=bucket,
            outpost_id=outpost_id,
            tags=tags,
            tags_all=tags_all,
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
    @jsii.member(jsii_name="creationDate")
    def creation_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccessBlockEnabled")
    def public_access_block_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "publicAccessBlockEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outpostIdInput")
    def outpost_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outpostIdInput"))

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
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outpostId")
    def outpost_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outpostId"))

    @outpost_id.setter
    def outpost_id(self, value: builtins.str) -> None:
        jsii.set(self, "outpostId", value)

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
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "outpost_id": "outpostId",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class S3ControlBucketConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        outpost_id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#bucket S3ControlBucket#bucket}.
        :param outpost_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#outpost_id S3ControlBucket#outpost_id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#tags S3ControlBucket#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#tags_all S3ControlBucket#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "outpost_id": outpost_id,
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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#bucket S3ControlBucket#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def outpost_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#outpost_id S3ControlBucket#outpost_id}.'''
        result = self._values.get("outpost_id")
        assert result is not None, "Required property 'outpost_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#tags S3ControlBucket#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket#tags_all S3ControlBucket#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlBucketConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlBucketLifecycleConfiguration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketLifecycleConfiguration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration aws_s3control_bucket_lifecycle_configuration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        rule: typing.Sequence["S3ControlBucketLifecycleConfigurationRule"],
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration aws_s3control_bucket_lifecycle_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#bucket S3ControlBucketLifecycleConfiguration#bucket}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#rule S3ControlBucketLifecycleConfiguration#rule}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3ControlBucketLifecycleConfigurationConfig(
            bucket=bucket,
            rule=rule,
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
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleInput")
    def rule_input(
        self,
    ) -> typing.Optional[typing.List["S3ControlBucketLifecycleConfigurationRule"]]:
        return typing.cast(typing.Optional[typing.List["S3ControlBucketLifecycleConfigurationRule"]], jsii.get(self, "ruleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rule")
    def rule(self) -> typing.List["S3ControlBucketLifecycleConfigurationRule"]:
        return typing.cast(typing.List["S3ControlBucketLifecycleConfigurationRule"], jsii.get(self, "rule"))

    @rule.setter
    def rule(
        self,
        value: typing.List["S3ControlBucketLifecycleConfigurationRule"],
    ) -> None:
        jsii.set(self, "rule", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketLifecycleConfigurationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "rule": "rule",
    },
)
class S3ControlBucketLifecycleConfigurationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        rule: typing.Sequence["S3ControlBucketLifecycleConfigurationRule"],
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#bucket S3ControlBucketLifecycleConfiguration#bucket}.
        :param rule: rule block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#rule S3ControlBucketLifecycleConfiguration#rule}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "rule": rule,
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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#bucket S3ControlBucketLifecycleConfiguration#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule(self) -> typing.List["S3ControlBucketLifecycleConfigurationRule"]:
        '''rule block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#rule S3ControlBucketLifecycleConfiguration#rule}
        '''
        result = self._values.get("rule")
        assert result is not None, "Required property 'rule' is missing"
        return typing.cast(typing.List["S3ControlBucketLifecycleConfigurationRule"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlBucketLifecycleConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketLifecycleConfigurationRule",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "abort_incomplete_multipart_upload": "abortIncompleteMultipartUpload",
        "expiration": "expiration",
        "filter": "filter",
        "status": "status",
    },
)
class S3ControlBucketLifecycleConfigurationRule:
    def __init__(
        self,
        *,
        id: builtins.str,
        abort_incomplete_multipart_upload: typing.Optional["S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload"] = None,
        expiration: typing.Optional["S3ControlBucketLifecycleConfigurationRuleExpiration"] = None,
        filter: typing.Optional["S3ControlBucketLifecycleConfigurationRuleFilter"] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#id S3ControlBucketLifecycleConfiguration#id}.
        :param abort_incomplete_multipart_upload: abort_incomplete_multipart_upload block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#abort_incomplete_multipart_upload S3ControlBucketLifecycleConfiguration#abort_incomplete_multipart_upload}
        :param expiration: expiration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#expiration S3ControlBucketLifecycleConfiguration#expiration}
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#filter S3ControlBucketLifecycleConfiguration#filter}
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#status S3ControlBucketLifecycleConfiguration#status}.
        '''
        if isinstance(abort_incomplete_multipart_upload, dict):
            abort_incomplete_multipart_upload = S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload(**abort_incomplete_multipart_upload)
        if isinstance(expiration, dict):
            expiration = S3ControlBucketLifecycleConfigurationRuleExpiration(**expiration)
        if isinstance(filter, dict):
            filter = S3ControlBucketLifecycleConfigurationRuleFilter(**filter)
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }
        if abort_incomplete_multipart_upload is not None:
            self._values["abort_incomplete_multipart_upload"] = abort_incomplete_multipart_upload
        if expiration is not None:
            self._values["expiration"] = expiration
        if filter is not None:
            self._values["filter"] = filter
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#id S3ControlBucketLifecycleConfiguration#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def abort_incomplete_multipart_upload(
        self,
    ) -> typing.Optional["S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload"]:
        '''abort_incomplete_multipart_upload block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#abort_incomplete_multipart_upload S3ControlBucketLifecycleConfiguration#abort_incomplete_multipart_upload}
        '''
        result = self._values.get("abort_incomplete_multipart_upload")
        return typing.cast(typing.Optional["S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload"], result)

    @builtins.property
    def expiration(
        self,
    ) -> typing.Optional["S3ControlBucketLifecycleConfigurationRuleExpiration"]:
        '''expiration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#expiration S3ControlBucketLifecycleConfiguration#expiration}
        '''
        result = self._values.get("expiration")
        return typing.cast(typing.Optional["S3ControlBucketLifecycleConfigurationRuleExpiration"], result)

    @builtins.property
    def filter(
        self,
    ) -> typing.Optional["S3ControlBucketLifecycleConfigurationRuleFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#filter S3ControlBucketLifecycleConfiguration#filter}
        '''
        result = self._values.get("filter")
        return typing.cast(typing.Optional["S3ControlBucketLifecycleConfigurationRuleFilter"], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#status S3ControlBucketLifecycleConfiguration#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlBucketLifecycleConfigurationRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload",
    jsii_struct_bases=[],
    name_mapping={"days_after_initiation": "daysAfterInitiation"},
)
class S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload:
    def __init__(self, *, days_after_initiation: jsii.Number) -> None:
        '''
        :param days_after_initiation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#days_after_initiation S3ControlBucketLifecycleConfiguration#days_after_initiation}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "days_after_initiation": days_after_initiation,
        }

    @builtins.property
    def days_after_initiation(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#days_after_initiation S3ControlBucketLifecycleConfiguration#days_after_initiation}.'''
        result = self._values.get("days_after_initiation")
        assert result is not None, "Required property 'days_after_initiation' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUploadOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUploadOutputReference",
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
    @jsii.member(jsii_name="daysAfterInitiationInput")
    def days_after_initiation_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "daysAfterInitiationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="daysAfterInitiation")
    def days_after_initiation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "daysAfterInitiation"))

    @days_after_initiation.setter
    def days_after_initiation(self, value: jsii.Number) -> None:
        jsii.set(self, "daysAfterInitiation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload]:
        return typing.cast(typing.Optional[S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketLifecycleConfigurationRuleExpiration",
    jsii_struct_bases=[],
    name_mapping={
        "date": "date",
        "days": "days",
        "expired_object_delete_marker": "expiredObjectDeleteMarker",
    },
)
class S3ControlBucketLifecycleConfigurationRuleExpiration:
    def __init__(
        self,
        *,
        date: typing.Optional[builtins.str] = None,
        days: typing.Optional[jsii.Number] = None,
        expired_object_delete_marker: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param date: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#date S3ControlBucketLifecycleConfiguration#date}.
        :param days: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#days S3ControlBucketLifecycleConfiguration#days}.
        :param expired_object_delete_marker: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#expired_object_delete_marker S3ControlBucketLifecycleConfiguration#expired_object_delete_marker}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if date is not None:
            self._values["date"] = date
        if days is not None:
            self._values["days"] = days
        if expired_object_delete_marker is not None:
            self._values["expired_object_delete_marker"] = expired_object_delete_marker

    @builtins.property
    def date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#date S3ControlBucketLifecycleConfiguration#date}.'''
        result = self._values.get("date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#days S3ControlBucketLifecycleConfiguration#days}.'''
        result = self._values.get("days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def expired_object_delete_marker(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#expired_object_delete_marker S3ControlBucketLifecycleConfiguration#expired_object_delete_marker}.'''
        result = self._values.get("expired_object_delete_marker")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlBucketLifecycleConfigurationRuleExpiration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlBucketLifecycleConfigurationRuleExpirationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketLifecycleConfigurationRuleExpirationOutputReference",
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

    @jsii.member(jsii_name="resetDate")
    def reset_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDate", []))

    @jsii.member(jsii_name="resetDays")
    def reset_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDays", []))

    @jsii.member(jsii_name="resetExpiredObjectDeleteMarker")
    def reset_expired_object_delete_marker(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpiredObjectDeleteMarker", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateInput")
    def date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="daysInput")
    def days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "daysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expiredObjectDeleteMarkerInput")
    def expired_object_delete_marker_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "expiredObjectDeleteMarkerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="date")
    def date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "date"))

    @date.setter
    def date(self, value: builtins.str) -> None:
        jsii.set(self, "date", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="days")
    def days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "days"))

    @days.setter
    def days(self, value: jsii.Number) -> None:
        jsii.set(self, "days", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expiredObjectDeleteMarker")
    def expired_object_delete_marker(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "expiredObjectDeleteMarker"))

    @expired_object_delete_marker.setter
    def expired_object_delete_marker(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "expiredObjectDeleteMarker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlBucketLifecycleConfigurationRuleExpiration]:
        return typing.cast(typing.Optional[S3ControlBucketLifecycleConfigurationRuleExpiration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlBucketLifecycleConfigurationRuleExpiration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketLifecycleConfigurationRuleFilter",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix", "tags": "tags"},
)
class S3ControlBucketLifecycleConfigurationRuleFilter:
    def __init__(
        self,
        *,
        prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#prefix S3ControlBucketLifecycleConfiguration#prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#tags S3ControlBucketLifecycleConfiguration#tags}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#prefix S3ControlBucketLifecycleConfiguration#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_lifecycle_configuration#tags S3ControlBucketLifecycleConfiguration#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlBucketLifecycleConfigurationRuleFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlBucketLifecycleConfigurationRuleFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketLifecycleConfigurationRuleFilterOutputReference",
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

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlBucketLifecycleConfigurationRuleFilter]:
        return typing.cast(typing.Optional[S3ControlBucketLifecycleConfigurationRuleFilter], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlBucketLifecycleConfigurationRuleFilter],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3ControlBucketPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_policy aws_s3control_bucket_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        policy: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_policy aws_s3control_bucket_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_policy#bucket S3ControlBucketPolicy#bucket}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_policy#policy S3ControlBucketPolicy#policy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3ControlBucketPolicyConfig(
            bucket=bucket,
            policy=policy,
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
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlBucketPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "policy": "policy",
    },
)
class S3ControlBucketPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        policy: builtins.str,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_policy#bucket S3ControlBucketPolicy#bucket}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_policy#policy S3ControlBucketPolicy#policy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "policy": policy,
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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_policy#bucket S3ControlBucketPolicy#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_bucket_policy#policy S3ControlBucketPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlBucketPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlMultiRegionAccessPoint(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point aws_s3control_multi_region_access_point}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        details: "S3ControlMultiRegionAccessPointDetails",
        account_id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["S3ControlMultiRegionAccessPointTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point aws_s3control_multi_region_access_point} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param details: details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#details S3ControlMultiRegionAccessPoint#details}
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#account_id S3ControlMultiRegionAccessPoint#account_id}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#timeouts S3ControlMultiRegionAccessPoint#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3ControlMultiRegionAccessPointConfig(
            details=details,
            account_id=account_id,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDetails")
    def put_details(
        self,
        *,
        name: builtins.str,
        region: typing.Sequence["S3ControlMultiRegionAccessPointDetailsRegion"],
        public_access_block: typing.Optional["S3ControlMultiRegionAccessPointDetailsPublicAccessBlock"] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#name S3ControlMultiRegionAccessPoint#name}.
        :param region: region block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#region S3ControlMultiRegionAccessPoint#region}
        :param public_access_block: public_access_block block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#public_access_block S3ControlMultiRegionAccessPoint#public_access_block}
        '''
        value = S3ControlMultiRegionAccessPointDetails(
            name=name, region=region, public_access_block=public_access_block
        )

        return typing.cast(None, jsii.invoke(self, "putDetails", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#create S3ControlMultiRegionAccessPoint#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#delete S3ControlMultiRegionAccessPoint#delete}.
        '''
        value = S3ControlMultiRegionAccessPointTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

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
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="details")
    def details(self) -> "S3ControlMultiRegionAccessPointDetailsOutputReference":
        return typing.cast("S3ControlMultiRegionAccessPointDetailsOutputReference", jsii.get(self, "details"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

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
    def timeouts(self) -> "S3ControlMultiRegionAccessPointTimeoutsOutputReference":
        return typing.cast("S3ControlMultiRegionAccessPointTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detailsInput")
    def details_input(
        self,
    ) -> typing.Optional["S3ControlMultiRegionAccessPointDetails"]:
        return typing.cast(typing.Optional["S3ControlMultiRegionAccessPointDetails"], jsii.get(self, "detailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional["S3ControlMultiRegionAccessPointTimeouts"]:
        return typing.cast(typing.Optional["S3ControlMultiRegionAccessPointTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "details": "details",
        "account_id": "accountId",
        "timeouts": "timeouts",
    },
)
class S3ControlMultiRegionAccessPointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        details: "S3ControlMultiRegionAccessPointDetails",
        account_id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["S3ControlMultiRegionAccessPointTimeouts"] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param details: details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#details S3ControlMultiRegionAccessPoint#details}
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#account_id S3ControlMultiRegionAccessPoint#account_id}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#timeouts S3ControlMultiRegionAccessPoint#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(details, dict):
            details = S3ControlMultiRegionAccessPointDetails(**details)
        if isinstance(timeouts, dict):
            timeouts = S3ControlMultiRegionAccessPointTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "details": details,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id
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
    def details(self) -> "S3ControlMultiRegionAccessPointDetails":
        '''details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#details S3ControlMultiRegionAccessPoint#details}
        '''
        result = self._values.get("details")
        assert result is not None, "Required property 'details' is missing"
        return typing.cast("S3ControlMultiRegionAccessPointDetails", result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#account_id S3ControlMultiRegionAccessPoint#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["S3ControlMultiRegionAccessPointTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#timeouts S3ControlMultiRegionAccessPoint#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["S3ControlMultiRegionAccessPointTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlMultiRegionAccessPointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointDetails",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "region": "region",
        "public_access_block": "publicAccessBlock",
    },
)
class S3ControlMultiRegionAccessPointDetails:
    def __init__(
        self,
        *,
        name: builtins.str,
        region: typing.Sequence["S3ControlMultiRegionAccessPointDetailsRegion"],
        public_access_block: typing.Optional["S3ControlMultiRegionAccessPointDetailsPublicAccessBlock"] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#name S3ControlMultiRegionAccessPoint#name}.
        :param region: region block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#region S3ControlMultiRegionAccessPoint#region}
        :param public_access_block: public_access_block block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#public_access_block S3ControlMultiRegionAccessPoint#public_access_block}
        '''
        if isinstance(public_access_block, dict):
            public_access_block = S3ControlMultiRegionAccessPointDetailsPublicAccessBlock(**public_access_block)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "region": region,
        }
        if public_access_block is not None:
            self._values["public_access_block"] = public_access_block

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#name S3ControlMultiRegionAccessPoint#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> typing.List["S3ControlMultiRegionAccessPointDetailsRegion"]:
        '''region block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#region S3ControlMultiRegionAccessPoint#region}
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(typing.List["S3ControlMultiRegionAccessPointDetailsRegion"], result)

    @builtins.property
    def public_access_block(
        self,
    ) -> typing.Optional["S3ControlMultiRegionAccessPointDetailsPublicAccessBlock"]:
        '''public_access_block block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#public_access_block S3ControlMultiRegionAccessPoint#public_access_block}
        '''
        result = self._values.get("public_access_block")
        return typing.cast(typing.Optional["S3ControlMultiRegionAccessPointDetailsPublicAccessBlock"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlMultiRegionAccessPointDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlMultiRegionAccessPointDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointDetailsOutputReference",
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

    @jsii.member(jsii_name="putPublicAccessBlock")
    def put_public_access_block(
        self,
        *,
        block_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restrict_public_buckets: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param block_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#block_public_acls S3ControlMultiRegionAccessPoint#block_public_acls}.
        :param block_public_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#block_public_policy S3ControlMultiRegionAccessPoint#block_public_policy}.
        :param ignore_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#ignore_public_acls S3ControlMultiRegionAccessPoint#ignore_public_acls}.
        :param restrict_public_buckets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#restrict_public_buckets S3ControlMultiRegionAccessPoint#restrict_public_buckets}.
        '''
        value = S3ControlMultiRegionAccessPointDetailsPublicAccessBlock(
            block_public_acls=block_public_acls,
            block_public_policy=block_public_policy,
            ignore_public_acls=ignore_public_acls,
            restrict_public_buckets=restrict_public_buckets,
        )

        return typing.cast(None, jsii.invoke(self, "putPublicAccessBlock", [value]))

    @jsii.member(jsii_name="resetPublicAccessBlock")
    def reset_public_access_block(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicAccessBlock", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccessBlock")
    def public_access_block(
        self,
    ) -> "S3ControlMultiRegionAccessPointDetailsPublicAccessBlockOutputReference":
        return typing.cast("S3ControlMultiRegionAccessPointDetailsPublicAccessBlockOutputReference", jsii.get(self, "publicAccessBlock"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicAccessBlockInput")
    def public_access_block_input(
        self,
    ) -> typing.Optional["S3ControlMultiRegionAccessPointDetailsPublicAccessBlock"]:
        return typing.cast(typing.Optional["S3ControlMultiRegionAccessPointDetailsPublicAccessBlock"], jsii.get(self, "publicAccessBlockInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(
        self,
    ) -> typing.Optional[typing.List["S3ControlMultiRegionAccessPointDetailsRegion"]]:
        return typing.cast(typing.Optional[typing.List["S3ControlMultiRegionAccessPointDetailsRegion"]], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> typing.List["S3ControlMultiRegionAccessPointDetailsRegion"]:
        return typing.cast(typing.List["S3ControlMultiRegionAccessPointDetailsRegion"], jsii.get(self, "region"))

    @region.setter
    def region(
        self,
        value: typing.List["S3ControlMultiRegionAccessPointDetailsRegion"],
    ) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[S3ControlMultiRegionAccessPointDetails]:
        return typing.cast(typing.Optional[S3ControlMultiRegionAccessPointDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlMultiRegionAccessPointDetails],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointDetailsPublicAccessBlock",
    jsii_struct_bases=[],
    name_mapping={
        "block_public_acls": "blockPublicAcls",
        "block_public_policy": "blockPublicPolicy",
        "ignore_public_acls": "ignorePublicAcls",
        "restrict_public_buckets": "restrictPublicBuckets",
    },
)
class S3ControlMultiRegionAccessPointDetailsPublicAccessBlock:
    def __init__(
        self,
        *,
        block_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        block_public_policy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ignore_public_acls: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restrict_public_buckets: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param block_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#block_public_acls S3ControlMultiRegionAccessPoint#block_public_acls}.
        :param block_public_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#block_public_policy S3ControlMultiRegionAccessPoint#block_public_policy}.
        :param ignore_public_acls: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#ignore_public_acls S3ControlMultiRegionAccessPoint#ignore_public_acls}.
        :param restrict_public_buckets: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#restrict_public_buckets S3ControlMultiRegionAccessPoint#restrict_public_buckets}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if block_public_acls is not None:
            self._values["block_public_acls"] = block_public_acls
        if block_public_policy is not None:
            self._values["block_public_policy"] = block_public_policy
        if ignore_public_acls is not None:
            self._values["ignore_public_acls"] = ignore_public_acls
        if restrict_public_buckets is not None:
            self._values["restrict_public_buckets"] = restrict_public_buckets

    @builtins.property
    def block_public_acls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#block_public_acls S3ControlMultiRegionAccessPoint#block_public_acls}.'''
        result = self._values.get("block_public_acls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def block_public_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#block_public_policy S3ControlMultiRegionAccessPoint#block_public_policy}.'''
        result = self._values.get("block_public_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ignore_public_acls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#ignore_public_acls S3ControlMultiRegionAccessPoint#ignore_public_acls}.'''
        result = self._values.get("ignore_public_acls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def restrict_public_buckets(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#restrict_public_buckets S3ControlMultiRegionAccessPoint#restrict_public_buckets}.'''
        result = self._values.get("restrict_public_buckets")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlMultiRegionAccessPointDetailsPublicAccessBlock(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlMultiRegionAccessPointDetailsPublicAccessBlockOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointDetailsPublicAccessBlockOutputReference",
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

    @jsii.member(jsii_name="resetBlockPublicAcls")
    def reset_block_public_acls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPublicAcls", []))

    @jsii.member(jsii_name="resetBlockPublicPolicy")
    def reset_block_public_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockPublicPolicy", []))

    @jsii.member(jsii_name="resetIgnorePublicAcls")
    def reset_ignore_public_acls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnorePublicAcls", []))

    @jsii.member(jsii_name="resetRestrictPublicBuckets")
    def reset_restrict_public_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictPublicBuckets", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicAclsInput")
    def block_public_acls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "blockPublicAclsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicPolicyInput")
    def block_public_policy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "blockPublicPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePublicAclsInput")
    def ignore_public_acls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ignorePublicAclsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictPublicBucketsInput")
    def restrict_public_buckets_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "restrictPublicBucketsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicAcls")
    def block_public_acls(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "blockPublicAcls"))

    @block_public_acls.setter
    def block_public_acls(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "blockPublicAcls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockPublicPolicy")
    def block_public_policy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "blockPublicPolicy"))

    @block_public_policy.setter
    def block_public_policy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "blockPublicPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignorePublicAcls")
    def ignore_public_acls(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ignorePublicAcls"))

    @ignore_public_acls.setter
    def ignore_public_acls(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ignorePublicAcls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictPublicBuckets")
    def restrict_public_buckets(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "restrictPublicBuckets"))

    @restrict_public_buckets.setter
    def restrict_public_buckets(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "restrictPublicBuckets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlMultiRegionAccessPointDetailsPublicAccessBlock]:
        return typing.cast(typing.Optional[S3ControlMultiRegionAccessPointDetailsPublicAccessBlock], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlMultiRegionAccessPointDetailsPublicAccessBlock],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointDetailsRegion",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket"},
)
class S3ControlMultiRegionAccessPointDetailsRegion:
    def __init__(self, *, bucket: builtins.str) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#bucket S3ControlMultiRegionAccessPoint#bucket}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#bucket S3ControlMultiRegionAccessPoint#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlMultiRegionAccessPointDetailsRegion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlMultiRegionAccessPointPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy aws_s3control_multi_region_access_point_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        details: "S3ControlMultiRegionAccessPointPolicyDetails",
        account_id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["S3ControlMultiRegionAccessPointPolicyTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy aws_s3control_multi_region_access_point_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param details: details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#details S3ControlMultiRegionAccessPointPolicy#details}
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#account_id S3ControlMultiRegionAccessPointPolicy#account_id}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#timeouts S3ControlMultiRegionAccessPointPolicy#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3ControlMultiRegionAccessPointPolicyConfig(
            details=details,
            account_id=account_id,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDetails")
    def put_details(self, *, name: builtins.str, policy: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#name S3ControlMultiRegionAccessPointPolicy#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#policy S3ControlMultiRegionAccessPointPolicy#policy}.
        '''
        value = S3ControlMultiRegionAccessPointPolicyDetails(name=name, policy=policy)

        return typing.cast(None, jsii.invoke(self, "putDetails", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#create S3ControlMultiRegionAccessPointPolicy#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#update S3ControlMultiRegionAccessPointPolicy#update}.
        '''
        value = S3ControlMultiRegionAccessPointPolicyTimeouts(
            create=create, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

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
    @jsii.member(jsii_name="details")
    def details(self) -> "S3ControlMultiRegionAccessPointPolicyDetailsOutputReference":
        return typing.cast("S3ControlMultiRegionAccessPointPolicyDetailsOutputReference", jsii.get(self, "details"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="established")
    def established(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "established"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="proposed")
    def proposed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "proposed"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(
        self,
    ) -> "S3ControlMultiRegionAccessPointPolicyTimeoutsOutputReference":
        return typing.cast("S3ControlMultiRegionAccessPointPolicyTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detailsInput")
    def details_input(
        self,
    ) -> typing.Optional["S3ControlMultiRegionAccessPointPolicyDetails"]:
        return typing.cast(typing.Optional["S3ControlMultiRegionAccessPointPolicyDetails"], jsii.get(self, "detailsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional["S3ControlMultiRegionAccessPointPolicyTimeouts"]:
        return typing.cast(typing.Optional["S3ControlMultiRegionAccessPointPolicyTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "details": "details",
        "account_id": "accountId",
        "timeouts": "timeouts",
    },
)
class S3ControlMultiRegionAccessPointPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        details: "S3ControlMultiRegionAccessPointPolicyDetails",
        account_id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["S3ControlMultiRegionAccessPointPolicyTimeouts"] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param details: details block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#details S3ControlMultiRegionAccessPointPolicy#details}
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#account_id S3ControlMultiRegionAccessPointPolicy#account_id}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#timeouts S3ControlMultiRegionAccessPointPolicy#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(details, dict):
            details = S3ControlMultiRegionAccessPointPolicyDetails(**details)
        if isinstance(timeouts, dict):
            timeouts = S3ControlMultiRegionAccessPointPolicyTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "details": details,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id
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
    def details(self) -> "S3ControlMultiRegionAccessPointPolicyDetails":
        '''details block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#details S3ControlMultiRegionAccessPointPolicy#details}
        '''
        result = self._values.get("details")
        assert result is not None, "Required property 'details' is missing"
        return typing.cast("S3ControlMultiRegionAccessPointPolicyDetails", result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#account_id S3ControlMultiRegionAccessPointPolicy#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(
        self,
    ) -> typing.Optional["S3ControlMultiRegionAccessPointPolicyTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#timeouts S3ControlMultiRegionAccessPointPolicy#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["S3ControlMultiRegionAccessPointPolicyTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlMultiRegionAccessPointPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointPolicyDetails",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "policy": "policy"},
)
class S3ControlMultiRegionAccessPointPolicyDetails:
    def __init__(self, *, name: builtins.str, policy: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#name S3ControlMultiRegionAccessPointPolicy#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#policy S3ControlMultiRegionAccessPointPolicy#policy}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "policy": policy,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#name S3ControlMultiRegionAccessPointPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#policy S3ControlMultiRegionAccessPointPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlMultiRegionAccessPointPolicyDetails(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlMultiRegionAccessPointPolicyDetailsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointPolicyDetailsOutputReference",
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
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlMultiRegionAccessPointPolicyDetails]:
        return typing.cast(typing.Optional[S3ControlMultiRegionAccessPointPolicyDetails], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlMultiRegionAccessPointPolicyDetails],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointPolicyTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "update": "update"},
)
class S3ControlMultiRegionAccessPointPolicyTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#create S3ControlMultiRegionAccessPointPolicy#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#update S3ControlMultiRegionAccessPointPolicy#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#create S3ControlMultiRegionAccessPointPolicy#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point_policy#update S3ControlMultiRegionAccessPointPolicy#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlMultiRegionAccessPointPolicyTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlMultiRegionAccessPointPolicyTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointPolicyTimeoutsOutputReference",
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
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlMultiRegionAccessPointPolicyTimeouts]:
        return typing.cast(typing.Optional[S3ControlMultiRegionAccessPointPolicyTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlMultiRegionAccessPointPolicyTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class S3ControlMultiRegionAccessPointTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#create S3ControlMultiRegionAccessPoint#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#delete S3ControlMultiRegionAccessPoint#delete}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#create S3ControlMultiRegionAccessPoint#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_multi_region_access_point#delete S3ControlMultiRegionAccessPoint#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlMultiRegionAccessPointTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlMultiRegionAccessPointTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlMultiRegionAccessPointTimeoutsOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

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
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlMultiRegionAccessPointTimeouts]:
        return typing.cast(typing.Optional[S3ControlMultiRegionAccessPointTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlMultiRegionAccessPointTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3ControlObjectLambdaAccessPoint(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point aws_s3control_object_lambda_access_point}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        configuration: "S3ControlObjectLambdaAccessPointConfiguration",
        name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point aws_s3control_object_lambda_access_point} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#configuration S3ControlObjectLambdaAccessPoint#configuration}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#name S3ControlObjectLambdaAccessPoint#name}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#account_id S3ControlObjectLambdaAccessPoint#account_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3ControlObjectLambdaAccessPointConfig(
            configuration=configuration,
            name=name,
            account_id=account_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putConfiguration")
    def put_configuration(
        self,
        *,
        supporting_access_point: builtins.str,
        transformation_configuration: typing.Sequence["S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration"],
        allowed_features: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloud_watch_metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param supporting_access_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#supporting_access_point S3ControlObjectLambdaAccessPoint#supporting_access_point}.
        :param transformation_configuration: transformation_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#transformation_configuration S3ControlObjectLambdaAccessPoint#transformation_configuration}
        :param allowed_features: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#allowed_features S3ControlObjectLambdaAccessPoint#allowed_features}.
        :param cloud_watch_metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#cloud_watch_metrics_enabled S3ControlObjectLambdaAccessPoint#cloud_watch_metrics_enabled}.
        '''
        value = S3ControlObjectLambdaAccessPointConfiguration(
            supporting_access_point=supporting_access_point,
            transformation_configuration=transformation_configuration,
            allowed_features=allowed_features,
            cloud_watch_metrics_enabled=cloud_watch_metrics_enabled,
        )

        return typing.cast(None, jsii.invoke(self, "putConfiguration", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

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
    @jsii.member(jsii_name="configuration")
    def configuration(
        self,
    ) -> "S3ControlObjectLambdaAccessPointConfigurationOutputReference":
        return typing.cast("S3ControlObjectLambdaAccessPointConfigurationOutputReference", jsii.get(self, "configuration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationInput")
    def configuration_input(
        self,
    ) -> typing.Optional["S3ControlObjectLambdaAccessPointConfiguration"]:
        return typing.cast(typing.Optional["S3ControlObjectLambdaAccessPointConfiguration"], jsii.get(self, "configurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "configuration": "configuration",
        "name": "name",
        "account_id": "accountId",
    },
)
class S3ControlObjectLambdaAccessPointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        configuration: "S3ControlObjectLambdaAccessPointConfiguration",
        name: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param configuration: configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#configuration S3ControlObjectLambdaAccessPoint#configuration}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#name S3ControlObjectLambdaAccessPoint#name}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#account_id S3ControlObjectLambdaAccessPoint#account_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(configuration, dict):
            configuration = S3ControlObjectLambdaAccessPointConfiguration(**configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "configuration": configuration,
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
        if account_id is not None:
            self._values["account_id"] = account_id

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
    def configuration(self) -> "S3ControlObjectLambdaAccessPointConfiguration":
        '''configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#configuration S3ControlObjectLambdaAccessPoint#configuration}
        '''
        result = self._values.get("configuration")
        assert result is not None, "Required property 'configuration' is missing"
        return typing.cast("S3ControlObjectLambdaAccessPointConfiguration", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#name S3ControlObjectLambdaAccessPoint#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#account_id S3ControlObjectLambdaAccessPoint#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlObjectLambdaAccessPointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "supporting_access_point": "supportingAccessPoint",
        "transformation_configuration": "transformationConfiguration",
        "allowed_features": "allowedFeatures",
        "cloud_watch_metrics_enabled": "cloudWatchMetricsEnabled",
    },
)
class S3ControlObjectLambdaAccessPointConfiguration:
    def __init__(
        self,
        *,
        supporting_access_point: builtins.str,
        transformation_configuration: typing.Sequence["S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration"],
        allowed_features: typing.Optional[typing.Sequence[builtins.str]] = None,
        cloud_watch_metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param supporting_access_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#supporting_access_point S3ControlObjectLambdaAccessPoint#supporting_access_point}.
        :param transformation_configuration: transformation_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#transformation_configuration S3ControlObjectLambdaAccessPoint#transformation_configuration}
        :param allowed_features: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#allowed_features S3ControlObjectLambdaAccessPoint#allowed_features}.
        :param cloud_watch_metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#cloud_watch_metrics_enabled S3ControlObjectLambdaAccessPoint#cloud_watch_metrics_enabled}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "supporting_access_point": supporting_access_point,
            "transformation_configuration": transformation_configuration,
        }
        if allowed_features is not None:
            self._values["allowed_features"] = allowed_features
        if cloud_watch_metrics_enabled is not None:
            self._values["cloud_watch_metrics_enabled"] = cloud_watch_metrics_enabled

    @builtins.property
    def supporting_access_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#supporting_access_point S3ControlObjectLambdaAccessPoint#supporting_access_point}.'''
        result = self._values.get("supporting_access_point")
        assert result is not None, "Required property 'supporting_access_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def transformation_configuration(
        self,
    ) -> typing.List["S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration"]:
        '''transformation_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#transformation_configuration S3ControlObjectLambdaAccessPoint#transformation_configuration}
        '''
        result = self._values.get("transformation_configuration")
        assert result is not None, "Required property 'transformation_configuration' is missing"
        return typing.cast(typing.List["S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration"], result)

    @builtins.property
    def allowed_features(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#allowed_features S3ControlObjectLambdaAccessPoint#allowed_features}.'''
        result = self._values.get("allowed_features")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cloud_watch_metrics_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#cloud_watch_metrics_enabled S3ControlObjectLambdaAccessPoint#cloud_watch_metrics_enabled}.'''
        result = self._values.get("cloud_watch_metrics_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlObjectLambdaAccessPointConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlObjectLambdaAccessPointConfigurationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointConfigurationOutputReference",
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

    @jsii.member(jsii_name="resetAllowedFeatures")
    def reset_allowed_features(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedFeatures", []))

    @jsii.member(jsii_name="resetCloudWatchMetricsEnabled")
    def reset_cloud_watch_metrics_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudWatchMetricsEnabled", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedFeaturesInput")
    def allowed_features_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedFeaturesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudWatchMetricsEnabledInput")
    def cloud_watch_metrics_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "cloudWatchMetricsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportingAccessPointInput")
    def supporting_access_point_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "supportingAccessPointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transformationConfigurationInput")
    def transformation_configuration_input(
        self,
    ) -> typing.Optional[typing.List["S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration"]]:
        return typing.cast(typing.Optional[typing.List["S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration"]], jsii.get(self, "transformationConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedFeatures")
    def allowed_features(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedFeatures"))

    @allowed_features.setter
    def allowed_features(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "allowedFeatures", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudWatchMetricsEnabled")
    def cloud_watch_metrics_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "cloudWatchMetricsEnabled"))

    @cloud_watch_metrics_enabled.setter
    def cloud_watch_metrics_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "cloudWatchMetricsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportingAccessPoint")
    def supporting_access_point(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "supportingAccessPoint"))

    @supporting_access_point.setter
    def supporting_access_point(self, value: builtins.str) -> None:
        jsii.set(self, "supportingAccessPoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transformationConfiguration")
    def transformation_configuration(
        self,
    ) -> typing.List["S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration"]:
        return typing.cast(typing.List["S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration"], jsii.get(self, "transformationConfiguration"))

    @transformation_configuration.setter
    def transformation_configuration(
        self,
        value: typing.List["S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration"],
    ) -> None:
        jsii.set(self, "transformationConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlObjectLambdaAccessPointConfiguration]:
        return typing.cast(typing.Optional[S3ControlObjectLambdaAccessPointConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlObjectLambdaAccessPointConfiguration],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "actions": "actions",
        "content_transformation": "contentTransformation",
    },
)
class S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration:
    def __init__(
        self,
        *,
        actions: typing.Sequence[builtins.str],
        content_transformation: "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation",
    ) -> None:
        '''
        :param actions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#actions S3ControlObjectLambdaAccessPoint#actions}.
        :param content_transformation: content_transformation block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#content_transformation S3ControlObjectLambdaAccessPoint#content_transformation}
        '''
        if isinstance(content_transformation, dict):
            content_transformation = S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation(**content_transformation)
        self._values: typing.Dict[str, typing.Any] = {
            "actions": actions,
            "content_transformation": content_transformation,
        }

    @builtins.property
    def actions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#actions S3ControlObjectLambdaAccessPoint#actions}.'''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def content_transformation(
        self,
    ) -> "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation":
        '''content_transformation block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#content_transformation S3ControlObjectLambdaAccessPoint#content_transformation}
        '''
        result = self._values.get("content_transformation")
        assert result is not None, "Required property 'content_transformation' is missing"
        return typing.cast("S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation",
    jsii_struct_bases=[],
    name_mapping={"aws_lambda": "awsLambda"},
)
class S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation:
    def __init__(
        self,
        *,
        aws_lambda: "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda",
    ) -> None:
        '''
        :param aws_lambda: aws_lambda block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#aws_lambda S3ControlObjectLambdaAccessPoint#aws_lambda}
        '''
        if isinstance(aws_lambda, dict):
            aws_lambda = S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda(**aws_lambda)
        self._values: typing.Dict[str, typing.Any] = {
            "aws_lambda": aws_lambda,
        }

    @builtins.property
    def aws_lambda(
        self,
    ) -> "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda":
        '''aws_lambda block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#aws_lambda S3ControlObjectLambdaAccessPoint#aws_lambda}
        '''
        result = self._values.get("aws_lambda")
        assert result is not None, "Required property 'aws_lambda' is missing"
        return typing.cast("S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda",
    jsii_struct_bases=[],
    name_mapping={
        "function_arn": "functionArn",
        "function_payload": "functionPayload",
    },
)
class S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda:
    def __init__(
        self,
        *,
        function_arn: builtins.str,
        function_payload: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#function_arn S3ControlObjectLambdaAccessPoint#function_arn}.
        :param function_payload: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#function_payload S3ControlObjectLambdaAccessPoint#function_payload}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function_arn": function_arn,
        }
        if function_payload is not None:
            self._values["function_payload"] = function_payload

    @builtins.property
    def function_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#function_arn S3ControlObjectLambdaAccessPoint#function_arn}.'''
        result = self._values.get("function_arn")
        assert result is not None, "Required property 'function_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_payload(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#function_payload S3ControlObjectLambdaAccessPoint#function_payload}.'''
        result = self._values.get("function_payload")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambdaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambdaOutputReference",
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

    @jsii.member(jsii_name="resetFunctionPayload")
    def reset_function_payload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctionPayload", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArnInput")
    def function_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionPayloadInput")
    def function_payload_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionPayloadInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @function_arn.setter
    def function_arn(self, value: builtins.str) -> None:
        jsii.set(self, "functionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionPayload")
    def function_payload(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionPayload"))

    @function_payload.setter
    def function_payload(self, value: builtins.str) -> None:
        jsii.set(self, "functionPayload", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda]:
        return typing.cast(typing.Optional[S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationOutputReference",
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

    @jsii.member(jsii_name="putAwsLambda")
    def put_aws_lambda(
        self,
        *,
        function_arn: builtins.str,
        function_payload: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#function_arn S3ControlObjectLambdaAccessPoint#function_arn}.
        :param function_payload: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point#function_payload S3ControlObjectLambdaAccessPoint#function_payload}.
        '''
        value = S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda(
            function_arn=function_arn, function_payload=function_payload
        )

        return typing.cast(None, jsii.invoke(self, "putAwsLambda", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsLambda")
    def aws_lambda(
        self,
    ) -> S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambdaOutputReference:
        return typing.cast(S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambdaOutputReference, jsii.get(self, "awsLambda"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsLambdaInput")
    def aws_lambda_input(
        self,
    ) -> typing.Optional[S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda]:
        return typing.cast(typing.Optional[S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda], jsii.get(self, "awsLambdaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation]:
        return typing.cast(typing.Optional[S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation],
    ) -> None:
        jsii.set(self, "internalValue", value)


class S3ControlObjectLambdaAccessPointPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy aws_s3control_object_lambda_access_point_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        policy: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy aws_s3control_object_lambda_access_point_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy#name S3ControlObjectLambdaAccessPointPolicy#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy#policy S3ControlObjectLambdaAccessPointPolicy#policy}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy#account_id S3ControlObjectLambdaAccessPointPolicy#account_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3ControlObjectLambdaAccessPointPolicyConfig(
            name=name,
            policy=policy,
            account_id=account_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasPublicAccessPolicy")
    def has_public_access_policy(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "hasPublicAccessPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ControlObjectLambdaAccessPointPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "policy": "policy",
        "account_id": "accountId",
    },
)
class S3ControlObjectLambdaAccessPointPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        policy: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy#name S3ControlObjectLambdaAccessPointPolicy#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy#policy S3ControlObjectLambdaAccessPointPolicy#policy}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy#account_id S3ControlObjectLambdaAccessPointPolicy#account_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "policy": policy,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy#name S3ControlObjectLambdaAccessPointPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy#policy S3ControlObjectLambdaAccessPointPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3control_object_lambda_access_point_policy#account_id S3ControlObjectLambdaAccessPointPolicy#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ControlObjectLambdaAccessPointPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3ObjectCopy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3ObjectCopy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy aws_s3_object_copy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        key: builtins.str,
        source: builtins.str,
        acl: typing.Optional[builtins.str] = None,
        bucket_key_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cache_control: typing.Optional[builtins.str] = None,
        content_disposition: typing.Optional[builtins.str] = None,
        content_encoding: typing.Optional[builtins.str] = None,
        content_language: typing.Optional[builtins.str] = None,
        content_type: typing.Optional[builtins.str] = None,
        copy_if_match: typing.Optional[builtins.str] = None,
        copy_if_modified_since: typing.Optional[builtins.str] = None,
        copy_if_none_match: typing.Optional[builtins.str] = None,
        copy_if_unmodified_since: typing.Optional[builtins.str] = None,
        customer_algorithm: typing.Optional[builtins.str] = None,
        customer_key: typing.Optional[builtins.str] = None,
        customer_key_md5: typing.Optional[builtins.str] = None,
        expected_bucket_owner: typing.Optional[builtins.str] = None,
        expected_source_bucket_owner: typing.Optional[builtins.str] = None,
        expires: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        grant: typing.Optional[typing.Sequence["S3ObjectCopyGrant"]] = None,
        kms_encryption_context: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        metadata_directive: typing.Optional[builtins.str] = None,
        object_lock_legal_hold_status: typing.Optional[builtins.str] = None,
        object_lock_mode: typing.Optional[builtins.str] = None,
        object_lock_retain_until_date: typing.Optional[builtins.str] = None,
        request_payer: typing.Optional[builtins.str] = None,
        server_side_encryption: typing.Optional[builtins.str] = None,
        source_customer_algorithm: typing.Optional[builtins.str] = None,
        source_customer_key: typing.Optional[builtins.str] = None,
        source_customer_key_md5: typing.Optional[builtins.str] = None,
        storage_class: typing.Optional[builtins.str] = None,
        tagging_directive: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        website_redirect: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy aws_s3_object_copy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#bucket S3ObjectCopy#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#key S3ObjectCopy#key}.
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source S3ObjectCopy#source}.
        :param acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#acl S3ObjectCopy#acl}.
        :param bucket_key_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#bucket_key_enabled S3ObjectCopy#bucket_key_enabled}.
        :param cache_control: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#cache_control S3ObjectCopy#cache_control}.
        :param content_disposition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_disposition S3ObjectCopy#content_disposition}.
        :param content_encoding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_encoding S3ObjectCopy#content_encoding}.
        :param content_language: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_language S3ObjectCopy#content_language}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_type S3ObjectCopy#content_type}.
        :param copy_if_match: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_match S3ObjectCopy#copy_if_match}.
        :param copy_if_modified_since: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_modified_since S3ObjectCopy#copy_if_modified_since}.
        :param copy_if_none_match: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_none_match S3ObjectCopy#copy_if_none_match}.
        :param copy_if_unmodified_since: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_unmodified_since S3ObjectCopy#copy_if_unmodified_since}.
        :param customer_algorithm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#customer_algorithm S3ObjectCopy#customer_algorithm}.
        :param customer_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#customer_key S3ObjectCopy#customer_key}.
        :param customer_key_md5: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#customer_key_md5 S3ObjectCopy#customer_key_md5}.
        :param expected_bucket_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#expected_bucket_owner S3ObjectCopy#expected_bucket_owner}.
        :param expected_source_bucket_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#expected_source_bucket_owner S3ObjectCopy#expected_source_bucket_owner}.
        :param expires: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#expires S3ObjectCopy#expires}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#force_destroy S3ObjectCopy#force_destroy}.
        :param grant: grant block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#grant S3ObjectCopy#grant}
        :param kms_encryption_context: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#kms_encryption_context S3ObjectCopy#kms_encryption_context}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#kms_key_id S3ObjectCopy#kms_key_id}.
        :param metadata: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#metadata S3ObjectCopy#metadata}.
        :param metadata_directive: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#metadata_directive S3ObjectCopy#metadata_directive}.
        :param object_lock_legal_hold_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#object_lock_legal_hold_status S3ObjectCopy#object_lock_legal_hold_status}.
        :param object_lock_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#object_lock_mode S3ObjectCopy#object_lock_mode}.
        :param object_lock_retain_until_date: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#object_lock_retain_until_date S3ObjectCopy#object_lock_retain_until_date}.
        :param request_payer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#request_payer S3ObjectCopy#request_payer}.
        :param server_side_encryption: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#server_side_encryption S3ObjectCopy#server_side_encryption}.
        :param source_customer_algorithm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source_customer_algorithm S3ObjectCopy#source_customer_algorithm}.
        :param source_customer_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source_customer_key S3ObjectCopy#source_customer_key}.
        :param source_customer_key_md5: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source_customer_key_md5 S3ObjectCopy#source_customer_key_md5}.
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#storage_class S3ObjectCopy#storage_class}.
        :param tagging_directive: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#tagging_directive S3ObjectCopy#tagging_directive}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#tags S3ObjectCopy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#tags_all S3ObjectCopy#tags_all}.
        :param website_redirect: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#website_redirect S3ObjectCopy#website_redirect}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3ObjectCopyConfig(
            bucket=bucket,
            key=key,
            source=source,
            acl=acl,
            bucket_key_enabled=bucket_key_enabled,
            cache_control=cache_control,
            content_disposition=content_disposition,
            content_encoding=content_encoding,
            content_language=content_language,
            content_type=content_type,
            copy_if_match=copy_if_match,
            copy_if_modified_since=copy_if_modified_since,
            copy_if_none_match=copy_if_none_match,
            copy_if_unmodified_since=copy_if_unmodified_since,
            customer_algorithm=customer_algorithm,
            customer_key=customer_key,
            customer_key_md5=customer_key_md5,
            expected_bucket_owner=expected_bucket_owner,
            expected_source_bucket_owner=expected_source_bucket_owner,
            expires=expires,
            force_destroy=force_destroy,
            grant=grant,
            kms_encryption_context=kms_encryption_context,
            kms_key_id=kms_key_id,
            metadata=metadata,
            metadata_directive=metadata_directive,
            object_lock_legal_hold_status=object_lock_legal_hold_status,
            object_lock_mode=object_lock_mode,
            object_lock_retain_until_date=object_lock_retain_until_date,
            request_payer=request_payer,
            server_side_encryption=server_side_encryption,
            source_customer_algorithm=source_customer_algorithm,
            source_customer_key=source_customer_key,
            source_customer_key_md5=source_customer_key_md5,
            storage_class=storage_class,
            tagging_directive=tagging_directive,
            tags=tags,
            tags_all=tags_all,
            website_redirect=website_redirect,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAcl")
    def reset_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAcl", []))

    @jsii.member(jsii_name="resetBucketKeyEnabled")
    def reset_bucket_key_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketKeyEnabled", []))

    @jsii.member(jsii_name="resetCacheControl")
    def reset_cache_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheControl", []))

    @jsii.member(jsii_name="resetContentDisposition")
    def reset_content_disposition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentDisposition", []))

    @jsii.member(jsii_name="resetContentEncoding")
    def reset_content_encoding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentEncoding", []))

    @jsii.member(jsii_name="resetContentLanguage")
    def reset_content_language(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentLanguage", []))

    @jsii.member(jsii_name="resetContentType")
    def reset_content_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentType", []))

    @jsii.member(jsii_name="resetCopyIfMatch")
    def reset_copy_if_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyIfMatch", []))

    @jsii.member(jsii_name="resetCopyIfModifiedSince")
    def reset_copy_if_modified_since(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyIfModifiedSince", []))

    @jsii.member(jsii_name="resetCopyIfNoneMatch")
    def reset_copy_if_none_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyIfNoneMatch", []))

    @jsii.member(jsii_name="resetCopyIfUnmodifiedSince")
    def reset_copy_if_unmodified_since(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyIfUnmodifiedSince", []))

    @jsii.member(jsii_name="resetCustomerAlgorithm")
    def reset_customer_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomerAlgorithm", []))

    @jsii.member(jsii_name="resetCustomerKey")
    def reset_customer_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomerKey", []))

    @jsii.member(jsii_name="resetCustomerKeyMd5")
    def reset_customer_key_md5(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomerKeyMd5", []))

    @jsii.member(jsii_name="resetExpectedBucketOwner")
    def reset_expected_bucket_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpectedBucketOwner", []))

    @jsii.member(jsii_name="resetExpectedSourceBucketOwner")
    def reset_expected_source_bucket_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpectedSourceBucketOwner", []))

    @jsii.member(jsii_name="resetExpires")
    def reset_expires(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpires", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetGrant")
    def reset_grant(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGrant", []))

    @jsii.member(jsii_name="resetKmsEncryptionContext")
    def reset_kms_encryption_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsEncryptionContext", []))

    @jsii.member(jsii_name="resetKmsKeyId")
    def reset_kms_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyId", []))

    @jsii.member(jsii_name="resetMetadata")
    def reset_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadata", []))

    @jsii.member(jsii_name="resetMetadataDirective")
    def reset_metadata_directive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadataDirective", []))

    @jsii.member(jsii_name="resetObjectLockLegalHoldStatus")
    def reset_object_lock_legal_hold_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockLegalHoldStatus", []))

    @jsii.member(jsii_name="resetObjectLockMode")
    def reset_object_lock_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockMode", []))

    @jsii.member(jsii_name="resetObjectLockRetainUntilDate")
    def reset_object_lock_retain_until_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockRetainUntilDate", []))

    @jsii.member(jsii_name="resetRequestPayer")
    def reset_request_payer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestPayer", []))

    @jsii.member(jsii_name="resetServerSideEncryption")
    def reset_server_side_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryption", []))

    @jsii.member(jsii_name="resetSourceCustomerAlgorithm")
    def reset_source_customer_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCustomerAlgorithm", []))

    @jsii.member(jsii_name="resetSourceCustomerKey")
    def reset_source_customer_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCustomerKey", []))

    @jsii.member(jsii_name="resetSourceCustomerKeyMd5")
    def reset_source_customer_key_md5(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCustomerKeyMd5", []))

    @jsii.member(jsii_name="resetStorageClass")
    def reset_storage_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageClass", []))

    @jsii.member(jsii_name="resetTaggingDirective")
    def reset_tagging_directive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaggingDirective", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetWebsiteRedirect")
    def reset_website_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebsiteRedirect", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expiration")
    def expiration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModified"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestCharged")
    def request_charged(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "requestCharged"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceVersionId")
    def source_version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceVersionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionId")
    def version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclInput")
    def acl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aclInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketKeyEnabledInput")
    def bucket_key_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "bucketKeyEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheControlInput")
    def cache_control_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheControlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentDispositionInput")
    def content_disposition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentDispositionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentEncodingInput")
    def content_encoding_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentEncodingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentLanguageInput")
    def content_language_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentLanguageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeInput")
    def content_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyIfMatchInput")
    def copy_if_match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyIfMatchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyIfModifiedSinceInput")
    def copy_if_modified_since_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyIfModifiedSinceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyIfNoneMatchInput")
    def copy_if_none_match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyIfNoneMatchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyIfUnmodifiedSinceInput")
    def copy_if_unmodified_since_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyIfUnmodifiedSinceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerAlgorithmInput")
    def customer_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerAlgorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerKeyInput")
    def customer_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerKeyMd5Input")
    def customer_key_md5_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerKeyMd5Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expectedBucketOwnerInput")
    def expected_bucket_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expectedBucketOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expectedSourceBucketOwnerInput")
    def expected_source_bucket_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expectedSourceBucketOwnerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expiresInput")
    def expires_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expiresInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantInput")
    def grant_input(self) -> typing.Optional[typing.List["S3ObjectCopyGrant"]]:
        return typing.cast(typing.Optional[typing.List["S3ObjectCopyGrant"]], jsii.get(self, "grantInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncryptionContextInput")
    def kms_encryption_context_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsEncryptionContextInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyIdInput")
    def kms_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadataDirectiveInput")
    def metadata_directive_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metadataDirectiveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "metadataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockLegalHoldStatusInput")
    def object_lock_legal_hold_status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockLegalHoldStatusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockModeInput")
    def object_lock_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockRetainUntilDateInput")
    def object_lock_retain_until_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockRetainUntilDateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestPayerInput")
    def request_payer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestPayerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryptionInput")
    def server_side_encryption_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverSideEncryptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCustomerAlgorithmInput")
    def source_customer_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCustomerAlgorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCustomerKeyInput")
    def source_customer_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCustomerKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCustomerKeyMd5Input")
    def source_customer_key_md5_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCustomerKeyMd5Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClassInput")
    def storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taggingDirectiveInput")
    def tagging_directive_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taggingDirectiveInput"))

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
    @jsii.member(jsii_name="websiteRedirectInput")
    def website_redirect_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "websiteRedirectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acl")
    def acl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acl"))

    @acl.setter
    def acl(self, value: builtins.str) -> None:
        jsii.set(self, "acl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketKeyEnabled")
    def bucket_key_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "bucketKeyEnabled"))

    @bucket_key_enabled.setter
    def bucket_key_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "bucketKeyEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheControl")
    def cache_control(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheControl"))

    @cache_control.setter
    def cache_control(self, value: builtins.str) -> None:
        jsii.set(self, "cacheControl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentDisposition")
    def content_disposition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentDisposition"))

    @content_disposition.setter
    def content_disposition(self, value: builtins.str) -> None:
        jsii.set(self, "contentDisposition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentEncoding")
    def content_encoding(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentEncoding"))

    @content_encoding.setter
    def content_encoding(self, value: builtins.str) -> None:
        jsii.set(self, "contentEncoding", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentLanguage")
    def content_language(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentLanguage"))

    @content_language.setter
    def content_language(self, value: builtins.str) -> None:
        jsii.set(self, "contentLanguage", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: builtins.str) -> None:
        jsii.set(self, "contentType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyIfMatch")
    def copy_if_match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copyIfMatch"))

    @copy_if_match.setter
    def copy_if_match(self, value: builtins.str) -> None:
        jsii.set(self, "copyIfMatch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyIfModifiedSince")
    def copy_if_modified_since(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copyIfModifiedSince"))

    @copy_if_modified_since.setter
    def copy_if_modified_since(self, value: builtins.str) -> None:
        jsii.set(self, "copyIfModifiedSince", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyIfNoneMatch")
    def copy_if_none_match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copyIfNoneMatch"))

    @copy_if_none_match.setter
    def copy_if_none_match(self, value: builtins.str) -> None:
        jsii.set(self, "copyIfNoneMatch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="copyIfUnmodifiedSince")
    def copy_if_unmodified_since(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copyIfUnmodifiedSince"))

    @copy_if_unmodified_since.setter
    def copy_if_unmodified_since(self, value: builtins.str) -> None:
        jsii.set(self, "copyIfUnmodifiedSince", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerAlgorithm")
    def customer_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerAlgorithm"))

    @customer_algorithm.setter
    def customer_algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "customerAlgorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerKey")
    def customer_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerKey"))

    @customer_key.setter
    def customer_key(self, value: builtins.str) -> None:
        jsii.set(self, "customerKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customerKeyMd5")
    def customer_key_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerKeyMd5"))

    @customer_key_md5.setter
    def customer_key_md5(self, value: builtins.str) -> None:
        jsii.set(self, "customerKeyMd5", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expectedBucketOwner")
    def expected_bucket_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expectedBucketOwner"))

    @expected_bucket_owner.setter
    def expected_bucket_owner(self, value: builtins.str) -> None:
        jsii.set(self, "expectedBucketOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expectedSourceBucketOwner")
    def expected_source_bucket_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expectedSourceBucketOwner"))

    @expected_source_bucket_owner.setter
    def expected_source_bucket_owner(self, value: builtins.str) -> None:
        jsii.set(self, "expectedSourceBucketOwner", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expires")
    def expires(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expires"))

    @expires.setter
    def expires(self, value: builtins.str) -> None:
        jsii.set(self, "expires", value)

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
    @jsii.member(jsii_name="grant")
    def grant(self) -> typing.List["S3ObjectCopyGrant"]:
        return typing.cast(typing.List["S3ObjectCopyGrant"], jsii.get(self, "grant"))

    @grant.setter
    def grant(self, value: typing.List["S3ObjectCopyGrant"]) -> None:
        jsii.set(self, "grant", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsEncryptionContext")
    def kms_encryption_context(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsEncryptionContext"))

    @kms_encryption_context.setter
    def kms_encryption_context(self, value: builtins.str) -> None:
        jsii.set(self, "kmsEncryptionContext", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadata")
    def metadata(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "metadata", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadataDirective")
    def metadata_directive(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metadataDirective"))

    @metadata_directive.setter
    def metadata_directive(self, value: builtins.str) -> None:
        jsii.set(self, "metadataDirective", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockLegalHoldStatus")
    def object_lock_legal_hold_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockLegalHoldStatus"))

    @object_lock_legal_hold_status.setter
    def object_lock_legal_hold_status(self, value: builtins.str) -> None:
        jsii.set(self, "objectLockLegalHoldStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockMode")
    def object_lock_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockMode"))

    @object_lock_mode.setter
    def object_lock_mode(self, value: builtins.str) -> None:
        jsii.set(self, "objectLockMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectLockRetainUntilDate")
    def object_lock_retain_until_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockRetainUntilDate"))

    @object_lock_retain_until_date.setter
    def object_lock_retain_until_date(self, value: builtins.str) -> None:
        jsii.set(self, "objectLockRetainUntilDate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestPayer")
    def request_payer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestPayer"))

    @request_payer.setter
    def request_payer(self, value: builtins.str) -> None:
        jsii.set(self, "requestPayer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverSideEncryption")
    def server_side_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverSideEncryption"))

    @server_side_encryption.setter
    def server_side_encryption(self, value: builtins.str) -> None:
        jsii.set(self, "serverSideEncryption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        jsii.set(self, "source", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCustomerAlgorithm")
    def source_customer_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCustomerAlgorithm"))

    @source_customer_algorithm.setter
    def source_customer_algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "sourceCustomerAlgorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCustomerKey")
    def source_customer_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCustomerKey"))

    @source_customer_key.setter
    def source_customer_key(self, value: builtins.str) -> None:
        jsii.set(self, "sourceCustomerKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceCustomerKeyMd5")
    def source_customer_key_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCustomerKeyMd5"))

    @source_customer_key_md5.setter
    def source_customer_key_md5(self, value: builtins.str) -> None:
        jsii.set(self, "sourceCustomerKeyMd5", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageClass")
    def storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageClass"))

    @storage_class.setter
    def storage_class(self, value: builtins.str) -> None:
        jsii.set(self, "storageClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taggingDirective")
    def tagging_directive(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taggingDirective"))

    @tagging_directive.setter
    def tagging_directive(self, value: builtins.str) -> None:
        jsii.set(self, "taggingDirective", value)

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
    @jsii.member(jsii_name="websiteRedirect")
    def website_redirect(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "websiteRedirect"))

    @website_redirect.setter
    def website_redirect(self, value: builtins.str) -> None:
        jsii.set(self, "websiteRedirect", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ObjectCopyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "bucket": "bucket",
        "key": "key",
        "source": "source",
        "acl": "acl",
        "bucket_key_enabled": "bucketKeyEnabled",
        "cache_control": "cacheControl",
        "content_disposition": "contentDisposition",
        "content_encoding": "contentEncoding",
        "content_language": "contentLanguage",
        "content_type": "contentType",
        "copy_if_match": "copyIfMatch",
        "copy_if_modified_since": "copyIfModifiedSince",
        "copy_if_none_match": "copyIfNoneMatch",
        "copy_if_unmodified_since": "copyIfUnmodifiedSince",
        "customer_algorithm": "customerAlgorithm",
        "customer_key": "customerKey",
        "customer_key_md5": "customerKeyMd5",
        "expected_bucket_owner": "expectedBucketOwner",
        "expected_source_bucket_owner": "expectedSourceBucketOwner",
        "expires": "expires",
        "force_destroy": "forceDestroy",
        "grant": "grant",
        "kms_encryption_context": "kmsEncryptionContext",
        "kms_key_id": "kmsKeyId",
        "metadata": "metadata",
        "metadata_directive": "metadataDirective",
        "object_lock_legal_hold_status": "objectLockLegalHoldStatus",
        "object_lock_mode": "objectLockMode",
        "object_lock_retain_until_date": "objectLockRetainUntilDate",
        "request_payer": "requestPayer",
        "server_side_encryption": "serverSideEncryption",
        "source_customer_algorithm": "sourceCustomerAlgorithm",
        "source_customer_key": "sourceCustomerKey",
        "source_customer_key_md5": "sourceCustomerKeyMd5",
        "storage_class": "storageClass",
        "tagging_directive": "taggingDirective",
        "tags": "tags",
        "tags_all": "tagsAll",
        "website_redirect": "websiteRedirect",
    },
)
class S3ObjectCopyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        bucket: builtins.str,
        key: builtins.str,
        source: builtins.str,
        acl: typing.Optional[builtins.str] = None,
        bucket_key_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        cache_control: typing.Optional[builtins.str] = None,
        content_disposition: typing.Optional[builtins.str] = None,
        content_encoding: typing.Optional[builtins.str] = None,
        content_language: typing.Optional[builtins.str] = None,
        content_type: typing.Optional[builtins.str] = None,
        copy_if_match: typing.Optional[builtins.str] = None,
        copy_if_modified_since: typing.Optional[builtins.str] = None,
        copy_if_none_match: typing.Optional[builtins.str] = None,
        copy_if_unmodified_since: typing.Optional[builtins.str] = None,
        customer_algorithm: typing.Optional[builtins.str] = None,
        customer_key: typing.Optional[builtins.str] = None,
        customer_key_md5: typing.Optional[builtins.str] = None,
        expected_bucket_owner: typing.Optional[builtins.str] = None,
        expected_source_bucket_owner: typing.Optional[builtins.str] = None,
        expires: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        grant: typing.Optional[typing.Sequence["S3ObjectCopyGrant"]] = None,
        kms_encryption_context: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        metadata_directive: typing.Optional[builtins.str] = None,
        object_lock_legal_hold_status: typing.Optional[builtins.str] = None,
        object_lock_mode: typing.Optional[builtins.str] = None,
        object_lock_retain_until_date: typing.Optional[builtins.str] = None,
        request_payer: typing.Optional[builtins.str] = None,
        server_side_encryption: typing.Optional[builtins.str] = None,
        source_customer_algorithm: typing.Optional[builtins.str] = None,
        source_customer_key: typing.Optional[builtins.str] = None,
        source_customer_key_md5: typing.Optional[builtins.str] = None,
        storage_class: typing.Optional[builtins.str] = None,
        tagging_directive: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        website_redirect: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#bucket S3ObjectCopy#bucket}.
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#key S3ObjectCopy#key}.
        :param source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source S3ObjectCopy#source}.
        :param acl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#acl S3ObjectCopy#acl}.
        :param bucket_key_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#bucket_key_enabled S3ObjectCopy#bucket_key_enabled}.
        :param cache_control: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#cache_control S3ObjectCopy#cache_control}.
        :param content_disposition: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_disposition S3ObjectCopy#content_disposition}.
        :param content_encoding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_encoding S3ObjectCopy#content_encoding}.
        :param content_language: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_language S3ObjectCopy#content_language}.
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_type S3ObjectCopy#content_type}.
        :param copy_if_match: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_match S3ObjectCopy#copy_if_match}.
        :param copy_if_modified_since: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_modified_since S3ObjectCopy#copy_if_modified_since}.
        :param copy_if_none_match: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_none_match S3ObjectCopy#copy_if_none_match}.
        :param copy_if_unmodified_since: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_unmodified_since S3ObjectCopy#copy_if_unmodified_since}.
        :param customer_algorithm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#customer_algorithm S3ObjectCopy#customer_algorithm}.
        :param customer_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#customer_key S3ObjectCopy#customer_key}.
        :param customer_key_md5: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#customer_key_md5 S3ObjectCopy#customer_key_md5}.
        :param expected_bucket_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#expected_bucket_owner S3ObjectCopy#expected_bucket_owner}.
        :param expected_source_bucket_owner: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#expected_source_bucket_owner S3ObjectCopy#expected_source_bucket_owner}.
        :param expires: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#expires S3ObjectCopy#expires}.
        :param force_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#force_destroy S3ObjectCopy#force_destroy}.
        :param grant: grant block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#grant S3ObjectCopy#grant}
        :param kms_encryption_context: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#kms_encryption_context S3ObjectCopy#kms_encryption_context}.
        :param kms_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#kms_key_id S3ObjectCopy#kms_key_id}.
        :param metadata: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#metadata S3ObjectCopy#metadata}.
        :param metadata_directive: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#metadata_directive S3ObjectCopy#metadata_directive}.
        :param object_lock_legal_hold_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#object_lock_legal_hold_status S3ObjectCopy#object_lock_legal_hold_status}.
        :param object_lock_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#object_lock_mode S3ObjectCopy#object_lock_mode}.
        :param object_lock_retain_until_date: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#object_lock_retain_until_date S3ObjectCopy#object_lock_retain_until_date}.
        :param request_payer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#request_payer S3ObjectCopy#request_payer}.
        :param server_side_encryption: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#server_side_encryption S3ObjectCopy#server_side_encryption}.
        :param source_customer_algorithm: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source_customer_algorithm S3ObjectCopy#source_customer_algorithm}.
        :param source_customer_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source_customer_key S3ObjectCopy#source_customer_key}.
        :param source_customer_key_md5: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source_customer_key_md5 S3ObjectCopy#source_customer_key_md5}.
        :param storage_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#storage_class S3ObjectCopy#storage_class}.
        :param tagging_directive: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#tagging_directive S3ObjectCopy#tagging_directive}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#tags S3ObjectCopy#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#tags_all S3ObjectCopy#tags_all}.
        :param website_redirect: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#website_redirect S3ObjectCopy#website_redirect}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "key": key,
            "source": source,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if acl is not None:
            self._values["acl"] = acl
        if bucket_key_enabled is not None:
            self._values["bucket_key_enabled"] = bucket_key_enabled
        if cache_control is not None:
            self._values["cache_control"] = cache_control
        if content_disposition is not None:
            self._values["content_disposition"] = content_disposition
        if content_encoding is not None:
            self._values["content_encoding"] = content_encoding
        if content_language is not None:
            self._values["content_language"] = content_language
        if content_type is not None:
            self._values["content_type"] = content_type
        if copy_if_match is not None:
            self._values["copy_if_match"] = copy_if_match
        if copy_if_modified_since is not None:
            self._values["copy_if_modified_since"] = copy_if_modified_since
        if copy_if_none_match is not None:
            self._values["copy_if_none_match"] = copy_if_none_match
        if copy_if_unmodified_since is not None:
            self._values["copy_if_unmodified_since"] = copy_if_unmodified_since
        if customer_algorithm is not None:
            self._values["customer_algorithm"] = customer_algorithm
        if customer_key is not None:
            self._values["customer_key"] = customer_key
        if customer_key_md5 is not None:
            self._values["customer_key_md5"] = customer_key_md5
        if expected_bucket_owner is not None:
            self._values["expected_bucket_owner"] = expected_bucket_owner
        if expected_source_bucket_owner is not None:
            self._values["expected_source_bucket_owner"] = expected_source_bucket_owner
        if expires is not None:
            self._values["expires"] = expires
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if grant is not None:
            self._values["grant"] = grant
        if kms_encryption_context is not None:
            self._values["kms_encryption_context"] = kms_encryption_context
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if metadata is not None:
            self._values["metadata"] = metadata
        if metadata_directive is not None:
            self._values["metadata_directive"] = metadata_directive
        if object_lock_legal_hold_status is not None:
            self._values["object_lock_legal_hold_status"] = object_lock_legal_hold_status
        if object_lock_mode is not None:
            self._values["object_lock_mode"] = object_lock_mode
        if object_lock_retain_until_date is not None:
            self._values["object_lock_retain_until_date"] = object_lock_retain_until_date
        if request_payer is not None:
            self._values["request_payer"] = request_payer
        if server_side_encryption is not None:
            self._values["server_side_encryption"] = server_side_encryption
        if source_customer_algorithm is not None:
            self._values["source_customer_algorithm"] = source_customer_algorithm
        if source_customer_key is not None:
            self._values["source_customer_key"] = source_customer_key
        if source_customer_key_md5 is not None:
            self._values["source_customer_key_md5"] = source_customer_key_md5
        if storage_class is not None:
            self._values["storage_class"] = storage_class
        if tagging_directive is not None:
            self._values["tagging_directive"] = tagging_directive
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if website_redirect is not None:
            self._values["website_redirect"] = website_redirect

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
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#bucket S3ObjectCopy#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#key S3ObjectCopy#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source S3ObjectCopy#source}.'''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def acl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#acl S3ObjectCopy#acl}.'''
        result = self._values.get("acl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_key_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#bucket_key_enabled S3ObjectCopy#bucket_key_enabled}.'''
        result = self._values.get("bucket_key_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def cache_control(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#cache_control S3ObjectCopy#cache_control}.'''
        result = self._values.get("cache_control")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_disposition(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_disposition S3ObjectCopy#content_disposition}.'''
        result = self._values.get("content_disposition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_encoding(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_encoding S3ObjectCopy#content_encoding}.'''
        result = self._values.get("content_encoding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_language(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_language S3ObjectCopy#content_language}.'''
        result = self._values.get("content_language")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#content_type S3ObjectCopy#content_type}.'''
        result = self._values.get("content_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_if_match(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_match S3ObjectCopy#copy_if_match}.'''
        result = self._values.get("copy_if_match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_if_modified_since(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_modified_since S3ObjectCopy#copy_if_modified_since}.'''
        result = self._values.get("copy_if_modified_since")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_if_none_match(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_none_match S3ObjectCopy#copy_if_none_match}.'''
        result = self._values.get("copy_if_none_match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_if_unmodified_since(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#copy_if_unmodified_since S3ObjectCopy#copy_if_unmodified_since}.'''
        result = self._values.get("copy_if_unmodified_since")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def customer_algorithm(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#customer_algorithm S3ObjectCopy#customer_algorithm}.'''
        result = self._values.get("customer_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def customer_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#customer_key S3ObjectCopy#customer_key}.'''
        result = self._values.get("customer_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def customer_key_md5(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#customer_key_md5 S3ObjectCopy#customer_key_md5}.'''
        result = self._values.get("customer_key_md5")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expected_bucket_owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#expected_bucket_owner S3ObjectCopy#expected_bucket_owner}.'''
        result = self._values.get("expected_bucket_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expected_source_bucket_owner(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#expected_source_bucket_owner S3ObjectCopy#expected_source_bucket_owner}.'''
        result = self._values.get("expected_source_bucket_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expires(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#expires S3ObjectCopy#expires}.'''
        result = self._values.get("expires")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#force_destroy S3ObjectCopy#force_destroy}.'''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def grant(self) -> typing.Optional[typing.List["S3ObjectCopyGrant"]]:
        '''grant block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#grant S3ObjectCopy#grant}
        '''
        result = self._values.get("grant")
        return typing.cast(typing.Optional[typing.List["S3ObjectCopyGrant"]], result)

    @builtins.property
    def kms_encryption_context(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#kms_encryption_context S3ObjectCopy#kms_encryption_context}.'''
        result = self._values.get("kms_encryption_context")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#kms_key_id S3ObjectCopy#kms_key_id}.'''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#metadata S3ObjectCopy#metadata}.'''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def metadata_directive(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#metadata_directive S3ObjectCopy#metadata_directive}.'''
        result = self._values.get("metadata_directive")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lock_legal_hold_status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#object_lock_legal_hold_status S3ObjectCopy#object_lock_legal_hold_status}.'''
        result = self._values.get("object_lock_legal_hold_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lock_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#object_lock_mode S3ObjectCopy#object_lock_mode}.'''
        result = self._values.get("object_lock_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lock_retain_until_date(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#object_lock_retain_until_date S3ObjectCopy#object_lock_retain_until_date}.'''
        result = self._values.get("object_lock_retain_until_date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_payer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#request_payer S3ObjectCopy#request_payer}.'''
        result = self._values.get("request_payer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_encryption(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#server_side_encryption S3ObjectCopy#server_side_encryption}.'''
        result = self._values.get("server_side_encryption")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_customer_algorithm(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source_customer_algorithm S3ObjectCopy#source_customer_algorithm}.'''
        result = self._values.get("source_customer_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_customer_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source_customer_key S3ObjectCopy#source_customer_key}.'''
        result = self._values.get("source_customer_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_customer_key_md5(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#source_customer_key_md5 S3ObjectCopy#source_customer_key_md5}.'''
        result = self._values.get("source_customer_key_md5")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#storage_class S3ObjectCopy#storage_class}.'''
        result = self._values.get("storage_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tagging_directive(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#tagging_directive S3ObjectCopy#tagging_directive}.'''
        result = self._values.get("tagging_directive")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#tags S3ObjectCopy#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#tags_all S3ObjectCopy#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def website_redirect(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#website_redirect S3ObjectCopy#website_redirect}.'''
        result = self._values.get("website_redirect")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ObjectCopyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3ObjectCopyGrant",
    jsii_struct_bases=[],
    name_mapping={
        "permissions": "permissions",
        "type": "type",
        "email": "email",
        "id": "id",
        "uri": "uri",
    },
)
class S3ObjectCopyGrant:
    def __init__(
        self,
        *,
        permissions: typing.Sequence[builtins.str],
        type: builtins.str,
        email: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param permissions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#permissions S3ObjectCopy#permissions}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#type S3ObjectCopy#type}.
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#email S3ObjectCopy#email}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#id S3ObjectCopy#id}.
        :param uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#uri S3ObjectCopy#uri}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "permissions": permissions,
            "type": type,
        }
        if email is not None:
            self._values["email"] = email
        if id is not None:
            self._values["id"] = id
        if uri is not None:
            self._values["uri"] = uri

    @builtins.property
    def permissions(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#permissions S3ObjectCopy#permissions}.'''
        result = self._values.get("permissions")
        assert result is not None, "Required property 'permissions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#type S3ObjectCopy#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#email S3ObjectCopy#email}.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#id S3ObjectCopy#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3_object_copy#uri S3ObjectCopy#uri}.'''
        result = self._values.get("uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ObjectCopyGrant(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3OutpostsEndpoint(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3OutpostsEndpoint",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint aws_s3outposts_endpoint}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        outpost_id: builtins.str,
        security_group_id: builtins.str,
        subnet_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint aws_s3outposts_endpoint} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param outpost_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint#outpost_id S3OutpostsEndpoint#outpost_id}.
        :param security_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint#security_group_id S3OutpostsEndpoint#security_group_id}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint#subnet_id S3OutpostsEndpoint#subnet_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = S3OutpostsEndpointConfig(
            outpost_id=outpost_id,
            security_group_id=security_group_id,
            subnet_id=subnet_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="networkInterfaces")
    def network_interfaces(
        self,
        index: builtins.str,
    ) -> "S3OutpostsEndpointNetworkInterfaces":
        '''
        :param index: -
        '''
        return typing.cast("S3OutpostsEndpointNetworkInterfaces", jsii.invoke(self, "networkInterfaces", [index]))

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
    @jsii.member(jsii_name="cidrBlock")
    def cidr_block(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cidrBlock"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outpostIdInput")
    def outpost_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outpostIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdInput")
    def security_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityGroupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdInput")
    def subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outpostId")
    def outpost_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outpostId"))

    @outpost_id.setter
    def outpost_id(self, value: builtins.str) -> None:
        jsii.set(self, "outpostId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupId")
    def security_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "securityGroupId"))

    @security_group_id.setter
    def security_group_id(self, value: builtins.str) -> None:
        jsii.set(self, "securityGroupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: builtins.str) -> None:
        jsii.set(self, "subnetId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.s3.S3OutpostsEndpointConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "outpost_id": "outpostId",
        "security_group_id": "securityGroupId",
        "subnet_id": "subnetId",
    },
)
class S3OutpostsEndpointConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        outpost_id: builtins.str,
        security_group_id: builtins.str,
        subnet_id: builtins.str,
    ) -> None:
        '''AWS Simple Storage Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param outpost_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint#outpost_id S3OutpostsEndpoint#outpost_id}.
        :param security_group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint#security_group_id S3OutpostsEndpoint#security_group_id}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint#subnet_id S3OutpostsEndpoint#subnet_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "outpost_id": outpost_id,
            "security_group_id": security_group_id,
            "subnet_id": subnet_id,
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
    def outpost_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint#outpost_id S3OutpostsEndpoint#outpost_id}.'''
        result = self._values.get("outpost_id")
        assert result is not None, "Required property 'outpost_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_group_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint#security_group_id S3OutpostsEndpoint#security_group_id}.'''
        result = self._values.get("security_group_id")
        assert result is not None, "Required property 'security_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/s3outposts_endpoint#subnet_id S3OutpostsEndpoint#subnet_id}.'''
        result = self._values.get("subnet_id")
        assert result is not None, "Required property 'subnet_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3OutpostsEndpointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3OutpostsEndpointNetworkInterfaces(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.s3.S3OutpostsEndpointNetworkInterfaces",
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
    @jsii.member(jsii_name="networkInterfaceId")
    def network_interface_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkInterfaceId"))


__all__ = [
    "DataAwsS3Bucket",
    "DataAwsS3BucketConfig",
    "DataAwsS3BucketObject",
    "DataAwsS3BucketObjectConfig",
    "DataAwsS3BucketObjects",
    "DataAwsS3BucketObjectsConfig",
    "S3AccessPoint",
    "S3AccessPointConfig",
    "S3AccessPointPublicAccessBlockConfiguration",
    "S3AccessPointPublicAccessBlockConfigurationOutputReference",
    "S3AccessPointVpcConfiguration",
    "S3AccessPointVpcConfigurationOutputReference",
    "S3AccountPublicAccessBlock",
    "S3AccountPublicAccessBlockConfig",
    "S3Bucket",
    "S3BucketAnalyticsConfiguration",
    "S3BucketAnalyticsConfigurationConfig",
    "S3BucketAnalyticsConfigurationFilter",
    "S3BucketAnalyticsConfigurationFilterOutputReference",
    "S3BucketAnalyticsConfigurationStorageClassAnalysis",
    "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExport",
    "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestination",
    "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationOutputReference",
    "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestination",
    "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportDestinationS3BucketDestinationOutputReference",
    "S3BucketAnalyticsConfigurationStorageClassAnalysisDataExportOutputReference",
    "S3BucketAnalyticsConfigurationStorageClassAnalysisOutputReference",
    "S3BucketConfig",
    "S3BucketCorsRule",
    "S3BucketGrant",
    "S3BucketIntelligentTieringConfiguration",
    "S3BucketIntelligentTieringConfigurationConfig",
    "S3BucketIntelligentTieringConfigurationFilter",
    "S3BucketIntelligentTieringConfigurationFilterOutputReference",
    "S3BucketIntelligentTieringConfigurationTiering",
    "S3BucketInventory",
    "S3BucketInventoryConfig",
    "S3BucketInventoryDestination",
    "S3BucketInventoryDestinationBucket",
    "S3BucketInventoryDestinationBucketEncryption",
    "S3BucketInventoryDestinationBucketEncryptionOutputReference",
    "S3BucketInventoryDestinationBucketEncryptionSseKms",
    "S3BucketInventoryDestinationBucketEncryptionSseKmsOutputReference",
    "S3BucketInventoryDestinationBucketEncryptionSseS3",
    "S3BucketInventoryDestinationBucketEncryptionSseS3OutputReference",
    "S3BucketInventoryDestinationBucketOutputReference",
    "S3BucketInventoryDestinationOutputReference",
    "S3BucketInventoryFilter",
    "S3BucketInventoryFilterOutputReference",
    "S3BucketInventorySchedule",
    "S3BucketInventoryScheduleOutputReference",
    "S3BucketLifecycleRule",
    "S3BucketLifecycleRuleExpiration",
    "S3BucketLifecycleRuleExpirationOutputReference",
    "S3BucketLifecycleRuleNoncurrentVersionExpiration",
    "S3BucketLifecycleRuleNoncurrentVersionExpirationOutputReference",
    "S3BucketLifecycleRuleNoncurrentVersionTransition",
    "S3BucketLifecycleRuleTransition",
    "S3BucketLogging",
    "S3BucketMetric",
    "S3BucketMetricConfig",
    "S3BucketMetricFilter",
    "S3BucketMetricFilterOutputReference",
    "S3BucketNotification",
    "S3BucketNotificationConfig",
    "S3BucketNotificationLambdaFunction",
    "S3BucketNotificationQueue",
    "S3BucketNotificationTopic",
    "S3BucketObject",
    "S3BucketObjectConfig",
    "S3BucketObjectLockConfiguration",
    "S3BucketObjectLockConfigurationOutputReference",
    "S3BucketObjectLockConfigurationRule",
    "S3BucketObjectLockConfigurationRuleDefaultRetention",
    "S3BucketObjectLockConfigurationRuleDefaultRetentionOutputReference",
    "S3BucketObjectLockConfigurationRuleOutputReference",
    "S3BucketOwnershipControls",
    "S3BucketOwnershipControlsConfig",
    "S3BucketOwnershipControlsRule",
    "S3BucketOwnershipControlsRuleOutputReference",
    "S3BucketPolicy",
    "S3BucketPolicyConfig",
    "S3BucketPublicAccessBlock",
    "S3BucketPublicAccessBlockConfig",
    "S3BucketReplicationConfiguration",
    "S3BucketReplicationConfigurationA",
    "S3BucketReplicationConfigurationAConfig",
    "S3BucketReplicationConfigurationOutputReference",
    "S3BucketReplicationConfigurationRule",
    "S3BucketReplicationConfigurationRuleDeleteMarkerReplication",
    "S3BucketReplicationConfigurationRuleDeleteMarkerReplicationOutputReference",
    "S3BucketReplicationConfigurationRuleDestination",
    "S3BucketReplicationConfigurationRuleDestinationAccessControlTranslation",
    "S3BucketReplicationConfigurationRuleDestinationAccessControlTranslationOutputReference",
    "S3BucketReplicationConfigurationRuleDestinationEncryptionConfiguration",
    "S3BucketReplicationConfigurationRuleDestinationEncryptionConfigurationOutputReference",
    "S3BucketReplicationConfigurationRuleDestinationMetrics",
    "S3BucketReplicationConfigurationRuleDestinationMetricsEventThreshold",
    "S3BucketReplicationConfigurationRuleDestinationMetricsEventThresholdOutputReference",
    "S3BucketReplicationConfigurationRuleDestinationMetricsOutputReference",
    "S3BucketReplicationConfigurationRuleDestinationOutputReference",
    "S3BucketReplicationConfigurationRuleDestinationReplicationTime",
    "S3BucketReplicationConfigurationRuleDestinationReplicationTimeOutputReference",
    "S3BucketReplicationConfigurationRuleDestinationReplicationTimeTime",
    "S3BucketReplicationConfigurationRuleDestinationReplicationTimeTimeOutputReference",
    "S3BucketReplicationConfigurationRuleExistingObjectReplication",
    "S3BucketReplicationConfigurationRuleExistingObjectReplicationOutputReference",
    "S3BucketReplicationConfigurationRuleFilter",
    "S3BucketReplicationConfigurationRuleFilterAnd",
    "S3BucketReplicationConfigurationRuleFilterAndOutputReference",
    "S3BucketReplicationConfigurationRuleFilterOutputReference",
    "S3BucketReplicationConfigurationRuleFilterTag",
    "S3BucketReplicationConfigurationRuleFilterTagOutputReference",
    "S3BucketReplicationConfigurationRuleSourceSelectionCriteria",
    "S3BucketReplicationConfigurationRuleSourceSelectionCriteriaOutputReference",
    "S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModifications",
    "S3BucketReplicationConfigurationRuleSourceSelectionCriteriaReplicaModificationsOutputReference",
    "S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjects",
    "S3BucketReplicationConfigurationRuleSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference",
    "S3BucketReplicationConfigurationRules",
    "S3BucketReplicationConfigurationRulesDestination",
    "S3BucketReplicationConfigurationRulesDestinationAccessControlTranslation",
    "S3BucketReplicationConfigurationRulesDestinationAccessControlTranslationOutputReference",
    "S3BucketReplicationConfigurationRulesDestinationMetrics",
    "S3BucketReplicationConfigurationRulesDestinationMetricsOutputReference",
    "S3BucketReplicationConfigurationRulesDestinationOutputReference",
    "S3BucketReplicationConfigurationRulesDestinationReplicationTime",
    "S3BucketReplicationConfigurationRulesDestinationReplicationTimeOutputReference",
    "S3BucketReplicationConfigurationRulesFilter",
    "S3BucketReplicationConfigurationRulesFilterOutputReference",
    "S3BucketReplicationConfigurationRulesSourceSelectionCriteria",
    "S3BucketReplicationConfigurationRulesSourceSelectionCriteriaOutputReference",
    "S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjects",
    "S3BucketReplicationConfigurationRulesSourceSelectionCriteriaSseKmsEncryptedObjectsOutputReference",
    "S3BucketServerSideEncryptionConfiguration",
    "S3BucketServerSideEncryptionConfigurationOutputReference",
    "S3BucketServerSideEncryptionConfigurationRule",
    "S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefault",
    "S3BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultOutputReference",
    "S3BucketServerSideEncryptionConfigurationRuleOutputReference",
    "S3BucketVersioning",
    "S3BucketVersioningOutputReference",
    "S3BucketWebsite",
    "S3BucketWebsiteOutputReference",
    "S3ControlAccessPointPolicy",
    "S3ControlAccessPointPolicyConfig",
    "S3ControlBucket",
    "S3ControlBucketConfig",
    "S3ControlBucketLifecycleConfiguration",
    "S3ControlBucketLifecycleConfigurationConfig",
    "S3ControlBucketLifecycleConfigurationRule",
    "S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUpload",
    "S3ControlBucketLifecycleConfigurationRuleAbortIncompleteMultipartUploadOutputReference",
    "S3ControlBucketLifecycleConfigurationRuleExpiration",
    "S3ControlBucketLifecycleConfigurationRuleExpirationOutputReference",
    "S3ControlBucketLifecycleConfigurationRuleFilter",
    "S3ControlBucketLifecycleConfigurationRuleFilterOutputReference",
    "S3ControlBucketPolicy",
    "S3ControlBucketPolicyConfig",
    "S3ControlMultiRegionAccessPoint",
    "S3ControlMultiRegionAccessPointConfig",
    "S3ControlMultiRegionAccessPointDetails",
    "S3ControlMultiRegionAccessPointDetailsOutputReference",
    "S3ControlMultiRegionAccessPointDetailsPublicAccessBlock",
    "S3ControlMultiRegionAccessPointDetailsPublicAccessBlockOutputReference",
    "S3ControlMultiRegionAccessPointDetailsRegion",
    "S3ControlMultiRegionAccessPointPolicy",
    "S3ControlMultiRegionAccessPointPolicyConfig",
    "S3ControlMultiRegionAccessPointPolicyDetails",
    "S3ControlMultiRegionAccessPointPolicyDetailsOutputReference",
    "S3ControlMultiRegionAccessPointPolicyTimeouts",
    "S3ControlMultiRegionAccessPointPolicyTimeoutsOutputReference",
    "S3ControlMultiRegionAccessPointTimeouts",
    "S3ControlMultiRegionAccessPointTimeoutsOutputReference",
    "S3ControlObjectLambdaAccessPoint",
    "S3ControlObjectLambdaAccessPointConfig",
    "S3ControlObjectLambdaAccessPointConfiguration",
    "S3ControlObjectLambdaAccessPointConfigurationOutputReference",
    "S3ControlObjectLambdaAccessPointConfigurationTransformationConfiguration",
    "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformation",
    "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambda",
    "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationAwsLambdaOutputReference",
    "S3ControlObjectLambdaAccessPointConfigurationTransformationConfigurationContentTransformationOutputReference",
    "S3ControlObjectLambdaAccessPointPolicy",
    "S3ControlObjectLambdaAccessPointPolicyConfig",
    "S3ObjectCopy",
    "S3ObjectCopyConfig",
    "S3ObjectCopyGrant",
    "S3OutpostsEndpoint",
    "S3OutpostsEndpointConfig",
    "S3OutpostsEndpointNetworkInterfaces",
]

publication.publish()
