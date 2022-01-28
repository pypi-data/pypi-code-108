'''
# cdk-library-renovo-s3-bucket

An AWS CDK construct library to create S3 buckets with some desirable defaults. Also provides some other helpers to make it easier to apply certain common rules we use.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_s3
import constructs


class RenovoS3Bucket(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-renovo-s3-bucket.RenovoS3Bucket",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        lifecycle_rules: typing.Sequence[aws_cdk.aws_s3.LifecycleRule],
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime.
        :param name: The name of the bucket.
        '''
        props = RenovoS3BucketProps(lifecycle_rules=lifecycle_rules, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.Bucket:
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "bucket"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-renovo-s3-bucket.RenovoS3BucketProps",
    jsii_struct_bases=[],
    name_mapping={"lifecycle_rules": "lifecycleRules", "name": "name"},
)
class RenovoS3BucketProps:
    def __init__(
        self,
        *,
        lifecycle_rules: typing.Sequence[aws_cdk.aws_s3.LifecycleRule],
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime.
        :param name: The name of the bucket.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "lifecycle_rules": lifecycle_rules,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def lifecycle_rules(self) -> typing.List[aws_cdk.aws_s3.LifecycleRule]:
        '''Rules that define how Amazon S3 manages objects during their lifetime.'''
        result = self._values.get("lifecycle_rules")
        assert result is not None, "Required property 'lifecycle_rules' is missing"
        return typing.cast(typing.List[aws_cdk.aws_s3.LifecycleRule], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the bucket.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RenovoS3BucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RenovoS3Bucket",
    "RenovoS3BucketProps",
]

publication.publish()
