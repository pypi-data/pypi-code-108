'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-dynamodb-seeder

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-dynamodb-seeder)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-dynamodb-seeder/)

> A seeder for dynamodb tables

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-dynamodb-seeder
```

Python:

```bash
pip install cloudcomponents.cdk-dynamodb-seeder
```

## How to use

```python
import * as path from 'path';
import { Construct, Stack, StackProps, RemovalPolicy } from '@aws-cdk/core';
import { Table, AttributeType } from '@aws-cdk/aws-dynamodb';
import { Bucket } from '@aws-cdk/aws-s3';
import { DynamoDBSeeder, Seeds } from '@cloudcomponents/cdk-dynamodb-seeder';

export class DynamoDBSeederStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const table = new Table(this, 'Table', {
      partitionKey: {
        name: 'id',
        type: AttributeType.NUMBER,
      },
      removalPolicy: RemovalPolicy.DESTROY,
    });

    new DynamoDBSeeder(this, 'JsonFileSeeder', {
      table,
      seeds: Seeds.fromJsonFile(path.join(__dirname, '..', 'seeds.json')),
    });

    new DynamoDBSeeder(this, 'InlineSeeder', {
      table,
      seeds: Seeds.fromInline([
        {
          id: 3,
          column: 'foo',
        },
        {
          id: 4,
          column: 'bar',
        },
      ]),
    });

    const seedsBucket = Bucket.fromBucketName(
      this,
      'SeedsBucket',
      'my-seeds-bucket',
    );

    new DynamoDBSeeder(this, 'BucketSeeder', {
      table,
      seeds: Seeds.fromBucket(seedsBucket, 'seeds.json'),
    });
  }
}
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-dynamodb-seeder/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-dynamodb-seeder/LICENSE)
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

import aws_cdk.assets
import aws_cdk.aws_dynamodb
import aws_cdk.aws_iam
import aws_cdk.aws_s3
import aws_cdk.aws_s3_assets
import aws_cdk.core


class DynamoDBSeeder(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-dynamodb-seeder.DynamoDBSeeder",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        seeds: "Seeds",
        table: aws_cdk.aws_dynamodb.ITable,
        timeout: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param seeds: -
        :param table: -
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.minutes(15)
        '''
        props = DynamoDBSeederProps(seeds=seeds, table=table, timeout=timeout)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-dynamodb-seeder.DynamoDBSeederProps",
    jsii_struct_bases=[],
    name_mapping={"seeds": "seeds", "table": "table", "timeout": "timeout"},
)
class DynamoDBSeederProps:
    def __init__(
        self,
        *,
        seeds: "Seeds",
        table: aws_cdk.aws_dynamodb.ITable,
        timeout: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param seeds: -
        :param table: -
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.minutes(15)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "seeds": seeds,
            "table": table,
        }
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def seeds(self) -> "Seeds":
        result = self._values.get("seeds")
        assert result is not None, "Required property 'seeds' is missing"
        return typing.cast("Seeds", result)

    @builtins.property
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(aws_cdk.aws_dynamodb.ITable, result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value
        based on the function's expected execution time.

        :default: Duration.minutes(15)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamoDBSeederProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Seeds(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cloudcomponents/cdk-dynamodb-seeder.Seeds",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromBucket") # type: ignore[misc]
    @builtins.classmethod
    def from_bucket(
        cls,
        bucket: aws_cdk.aws_s3.IBucket,
        key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> "S3Seeds":
        '''
        :param bucket: The S3 bucket.
        :param key: The object key.
        :param object_version: Optional S3 object version.

        :return: ``S3Seeds`` associated with the specified S3 object.
        '''
        return typing.cast("S3Seeds", jsii.sinvoke(cls, "fromBucket", [bucket, key, object_version]))

    @jsii.member(jsii_name="fromInline") # type: ignore[misc]
    @builtins.classmethod
    def from_inline(
        cls,
        seeds: typing.Sequence[typing.Mapping[builtins.str, typing.Any]],
    ) -> "InlineSeeds":
        '''
        :param seeds: The actual json code (limited to 4KiB).

        :return: ``InlineSeeds`` with inline seeds.
        '''
        return typing.cast("InlineSeeds", jsii.sinvoke(cls, "fromInline", [seeds]))

    @jsii.member(jsii_name="fromJsonFile") # type: ignore[misc]
    @builtins.classmethod
    def from_json_file(
        cls,
        path: builtins.str,
        *,
        readers: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IGrantable]] = None,
        source_hash: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow: typing.Optional[aws_cdk.assets.FollowMode] = None,
        ignore_mode: typing.Optional[aws_cdk.core.IgnoreMode] = None,
        follow_symlinks: typing.Optional[aws_cdk.core.SymlinkFollowMode] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[aws_cdk.core.AssetHashType] = None,
        bundling: typing.Optional[aws_cdk.core.BundlingOptions] = None,
    ) -> "JsonFileSeeds":
        '''Loads the seeds from a local disk path and uploads it to s3.

        :param path: Path to json seeds file.
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param source_hash: (deprecated) Custom hash to use when identifying the specific version of the asset. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the source hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the source hash, you will need to make sure it is updated every time the source changes, or otherwise it is possible that some deployments will not be invalidated. Default: - automatically calculate source hash based on the contents of the source file or directory.
        :param exclude: (deprecated) Glob patterns to exclude from the copy. Default: nothing is excluded
        :param follow: (deprecated) A strategy for how to handle symlinks. Default: Never
        :param ignore_mode: (deprecated) The ignore behavior to use for exclude patterns. Default: - GLOB for file assets, DOCKER or GLOB for docker assets depending on whether the '
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise

        :return: ``JsonFileSeeds`` associated with the specified S3 object.
        '''
        options = aws_cdk.aws_s3_assets.AssetOptions(
            readers=readers,
            source_hash=source_hash,
            exclude=exclude,
            follow=follow,
            ignore_mode=ignore_mode,
            follow_symlinks=follow_symlinks,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
        )

        return typing.cast("JsonFileSeeds", jsii.sinvoke(cls, "fromJsonFile", [path, options]))

    @jsii.member(jsii_name="bind") # type: ignore[misc]
    @abc.abstractmethod
    def bind(self, scope: aws_cdk.core.Construct) -> "SeedsConfig":
        '''Called when the seeder is initialized to allow this object to bind to the stack.

        :param scope: The binding scope.
        '''
        ...


class _SeedsProxy(Seeds):
    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct) -> "SeedsConfig":
        '''Called when the seeder is initialized to allow this object to bind to the stack.

        :param scope: The binding scope.
        '''
        return typing.cast("SeedsConfig", jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Seeds).__jsii_proxy_class__ = lambda : _SeedsProxy


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-dynamodb-seeder.SeedsConfig",
    jsii_struct_bases=[],
    name_mapping={"inline_seeds": "inlineSeeds", "s3_location": "s3Location"},
)
class SeedsConfig:
    def __init__(
        self,
        *,
        inline_seeds: typing.Optional[builtins.str] = None,
        s3_location: typing.Optional[aws_cdk.aws_s3.Location] = None,
    ) -> None:
        '''
        :param inline_seeds: Inline seeds.
        :param s3_location: The location of the seeds in S3.
        '''
        if isinstance(s3_location, dict):
            s3_location = aws_cdk.aws_s3.Location(**s3_location)
        self._values: typing.Dict[str, typing.Any] = {}
        if inline_seeds is not None:
            self._values["inline_seeds"] = inline_seeds
        if s3_location is not None:
            self._values["s3_location"] = s3_location

    @builtins.property
    def inline_seeds(self) -> typing.Optional[builtins.str]:
        '''Inline seeds.'''
        result = self._values.get("inline_seeds")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_location(self) -> typing.Optional[aws_cdk.aws_s3.Location]:
        '''The location of the seeds in S3.'''
        result = self._values.get("s3_location")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Location], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SeedsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InlineSeeds(
    Seeds,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-dynamodb-seeder.InlineSeeds",
):
    '''Seeds from an inline json object (limited to 4KiB).'''

    def __init__(self, seeds: builtins.str) -> None:
        '''
        :param seeds: -
        '''
        jsii.create(self.__class__, self, [seeds])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.core.Construct) -> SeedsConfig:
        '''Called when the seeder is initialized to allow this object to bind to the stack.

        :param _scope: -
        '''
        return typing.cast(SeedsConfig, jsii.invoke(self, "bind", [_scope]))


class JsonFileSeeds(
    Seeds,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-dynamodb-seeder.JsonFileSeeds",
):
    '''Seeds from a local json file.'''

    def __init__(
        self,
        path: builtins.str,
        *,
        readers: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IGrantable]] = None,
        source_hash: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow: typing.Optional[aws_cdk.assets.FollowMode] = None,
        ignore_mode: typing.Optional[aws_cdk.core.IgnoreMode] = None,
        follow_symlinks: typing.Optional[aws_cdk.core.SymlinkFollowMode] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[aws_cdk.core.AssetHashType] = None,
        bundling: typing.Optional[aws_cdk.core.BundlingOptions] = None,
    ) -> None:
        '''
        :param path: -
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param source_hash: (deprecated) Custom hash to use when identifying the specific version of the asset. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the source hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the source hash, you will need to make sure it is updated every time the source changes, or otherwise it is possible that some deployments will not be invalidated. Default: - automatically calculate source hash based on the contents of the source file or directory.
        :param exclude: (deprecated) Glob patterns to exclude from the copy. Default: nothing is excluded
        :param follow: (deprecated) A strategy for how to handle symlinks. Default: Never
        :param ignore_mode: (deprecated) The ignore behavior to use for exclude patterns. Default: - GLOB for file assets, DOCKER or GLOB for docker assets depending on whether the '
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise
        '''
        options = aws_cdk.aws_s3_assets.AssetOptions(
            readers=readers,
            source_hash=source_hash,
            exclude=exclude,
            follow=follow,
            ignore_mode=ignore_mode,
            follow_symlinks=follow_symlinks,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
        )

        jsii.create(self.__class__, self, [path, options])

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct) -> SeedsConfig:
        '''Called when the seeder is initialized to allow this object to bind to the stack.

        :param scope: -
        '''
        return typing.cast(SeedsConfig, jsii.invoke(self, "bind", [scope]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))


class S3Seeds(
    Seeds,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-dynamodb-seeder.S3Seeds",
):
    '''Seeds from an S3 archive.'''

    def __init__(
        self,
        bucket: aws_cdk.aws_s3.IBucket,
        key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: -
        :param key: -
        :param object_version: -
        '''
        jsii.create(self.__class__, self, [bucket, key, object_version])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.core.Construct) -> SeedsConfig:
        '''Called when the seeder is initialized to allow this object to bind to the stack.

        :param _scope: -
        '''
        return typing.cast(SeedsConfig, jsii.invoke(self, "bind", [_scope]))


__all__ = [
    "DynamoDBSeeder",
    "DynamoDBSeederProps",
    "InlineSeeds",
    "JsonFileSeeds",
    "S3Seeds",
    "Seeds",
    "SeedsConfig",
]

publication.publish()
