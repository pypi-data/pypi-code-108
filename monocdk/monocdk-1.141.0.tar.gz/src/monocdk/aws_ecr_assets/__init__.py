'''
# AWS CDK Docker Image Assets

This module allows bundling Docker images as assets.

## Images from Dockerfile

Images are built from a local Docker context directory (with a `Dockerfile`),
uploaded to Amazon Elastic Container Registry (ECR) by the CDK toolkit
and/or your app's CI/CD pipeline, and can be naturally referenced in your CDK app.

```python
from monocdk.aws_ecr_assets import DockerImageAsset


asset = DockerImageAsset(self, "MyBuildImage",
    directory=path.join(__dirname, "my-image")
)
```

The directory `my-image` must include a `Dockerfile`.

This will instruct the toolkit to build a Docker image from `my-image`, push it
to an Amazon ECR repository and wire the name of the repository as CloudFormation
parameters to your stack.

By default, all files in the given directory will be copied into the docker
*build context*. If there is a large directory that you know you definitely
don't need in the build context you can improve the performance by adding the
names of files and directories to ignore to a file called `.dockerignore`, or
pass them via the `exclude` property. If both are available, the patterns
found in `exclude` are appended to the patterns found in `.dockerignore`.

The `ignoreMode` property controls how the set of ignore patterns is
interpreted. The recommended setting for Docker image assets is
`IgnoreMode.DOCKER`. If the context flag
`@aws-cdk/aws-ecr-assets:dockerIgnoreSupport` is set to `true` in your
`cdk.json` (this is by default for new projects, but must be set manually for
old projects) then `IgnoreMode.DOCKER` is the default and you don't need to
configure it on the asset itself.

Use `asset.imageUri` to reference the image. It includes both the ECR image URL
and tag.

You can optionally pass build args to the `docker build` command by specifying
the `buildArgs` property. It is recommended to skip hashing of `buildArgs` for
values that can change between different machines to maintain a consistent
asset hash.

```python
from monocdk.aws_ecr_assets import DockerImageAsset


asset = DockerImageAsset(self, "MyBuildImage",
    directory=path.join(__dirname, "my-image"),
    build_args={
        "HTTP_PROXY": "http://10.20.30.2:1234"
    },
    invalidation=DockerImageAssetInvalidationOptions(
        build_args=False
    )
)
```

You can optionally pass a target to the `docker build` command by specifying
the `target` property:

```python
from monocdk.aws_ecr_assets import DockerImageAsset


asset = DockerImageAsset(self, "MyBuildImage",
    directory=path.join(__dirname, "my-image"),
    target="a-target"
)
```

## Images from Tarball

Images are loaded from a local tarball, uploaded to ECR by the CDK toolkit and/or your app's CI-CD pipeline, and can be
naturally referenced in your CDK app.

```python
from monocdk.aws_ecr_assets import TarballImageAsset


asset = TarballImageAsset(self, "MyBuildImage",
    tarball_file="local-image.tar"
)
```

This will instruct the toolkit to add the tarball as a file asset. During deployment it will load the container image
from `local-image.tar`, push it to an Amazon ECR repository and wire the name of the repository as CloudFormation parameters
to your stack.

## Publishing images to ECR repositories

`DockerImageAsset` is designed for seamless build & consumption of image assets by CDK code deployed to multiple environments
through the CDK CLI or through CI/CD workflows. To that end, the ECR repository behind this construct is controlled by the AWS CDK.
The mechanics of where these images are published and how are intentionally kept as an implementation detail, and the construct
does not support customizations such as specifying the ECR repository name or tags.

If you are looking for a way to *publish* image assets to an ECR repository in your control, you should consider using
[cdklabs/cdk-ecr-deployment](https://github.com/cdklabs/cdk-ecr-deployment), which is able to replicate an image asset from the CDK-controlled ECR repository to a repository of
your choice.

Here an example from the [cdklabs/cdk-ecr-deployment](https://github.com/cdklabs/cdk-ecr-deployment) project:

```text
// This example available in TypeScript only

import { DockerImageAsset } from 'monocdk/aws-ecr-assets';
import * as ecrdeploy from 'cdk-ecr-deployment';

const image = new DockerImageAsset(this, 'CDKDockerImage', {
  directory: path.join(__dirname, 'docker'),
});

new ecrdeploy.ECRDeployment(this, 'DeployDockerImage', {
  src: new ecrdeploy.DockerImageName(image.imageUri),
  dest: new ecrdeploy.DockerImageName(`${cdk.Aws.ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/test:nginx`),
});
```

⚠️ Please note that this is a 3rd-party construct library and is not officially supported by AWS.
You are welcome to +1 [this GitHub issue](https://github.com/aws/aws-cdk/issues/12597) if you would like to see
native support for this use-case in the AWS CDK.

## Pull Permissions

Depending on the consumer of your image asset, you will need to make sure
the principal has permissions to pull the image.

In most cases, you should use the `asset.repository.grantPull(principal)`
method. This will modify the IAM policy of the principal to allow it to
pull images from this repository.

If the pulling principal is not in the same account or is an AWS service that
doesn't assume a role in your account (e.g. AWS CodeBuild), pull permissions
must be granted on the **resource policy** (and not on the principal's policy).
To do that, you can use `asset.repository.addToResourcePolicy(statement)` to
grant the desired principal the following permissions: "ecr:GetDownloadUrlForLayer",
"ecr:BatchGetImage" and "ecr:BatchCheckLayerAvailability".
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from .. import (
    CfnResource as _CfnResource_e0a482dc,
    Construct as _Construct_e78e779f,
    FileFingerprintOptions as _FileFingerprintOptions_77e75a35,
    IgnoreMode as _IgnoreMode_31d8bf46,
    SymlinkFollowMode as _SymlinkFollowMode_abf4527a,
)
from ..assets import (
    FingerprintOptions as _FingerprintOptions_2f2cdaa3,
    FollowMode as _FollowMode_98b05cc5,
    IAsset as _IAsset_092a7035,
)
from ..aws_ecr import IRepository as _IRepository_8b4d2894


@jsii.implements(_IAsset_092a7035)
class DockerImageAsset(
    _Construct_e78e779f,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_ecr_assets.DockerImageAsset",
):
    '''(experimental) An asset that represents a Docker image.

    The image will be created in build time and uploaded to an ECR repository.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from monocdk.aws_ecr_assets import DockerImageAsset
        
        
        asset = DockerImageAsset(self, "MyBuildImage",
            directory=path.join(__dirname, "my-image"),
            build_args={
                "HTTP_PROXY": "http://10.20.30.2:1234"
            },
            invalidation=DockerImageAssetInvalidationOptions(
                build_args=False
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        directory: builtins.str,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        file: typing.Optional[builtins.str] = None,
        invalidation: typing.Optional["DockerImageAssetInvalidationOptions"] = None,
        repository_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        extra_hash: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow: typing.Optional[_FollowMode_98b05cc5] = None,
        ignore_mode: typing.Optional[_IgnoreMode_31d8bf46] = None,
        follow_symlinks: typing.Optional[_SymlinkFollowMode_abf4527a] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param directory: (experimental) The directory where the Dockerfile is stored. Any directory inside with a name that matches the CDK output folder (cdk.out by default) will be excluded from the asset
        :param build_args: (experimental) Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Default: - no build args are passed
        :param file: (experimental) Path to the Dockerfile (relative to the directory). Default: 'Dockerfile'
        :param invalidation: (experimental) Options to control which parameters are used to invalidate the asset hash. Default: - hash all parameters
        :param repository_name: (deprecated) ECR repository name. Specify this property if you need to statically address the image, e.g. from a Kubernetes Pod. Note, this is only the repository name, without the registry and the tag parts. Default: - the default ECR repository for CDK assets
        :param target: (experimental) Docker target to build to. Default: - no target
        :param extra_hash: (deprecated) Extra information to encode into the fingerprint (e.g. build instructions and other inputs). Default: - hash is only based on source content
        :param exclude: (deprecated) Glob patterns to exclude from the copy. Default: nothing is excluded
        :param follow: (deprecated) A strategy for how to handle symlinks. Default: Never
        :param ignore_mode: (deprecated) The ignore behavior to use for exclude patterns. Default: - GLOB for file assets, DOCKER or GLOB for docker assets depending on whether the '
        :param follow_symlinks: (experimental) A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER

        :stability: experimental
        '''
        props = DockerImageAssetProps(
            directory=directory,
            build_args=build_args,
            file=file,
            invalidation=invalidation,
            repository_name=repository_name,
            target=target,
            extra_hash=extra_hash,
            exclude=exclude,
            follow=follow,
            ignore_mode=ignore_mode,
            follow_symlinks=follow_symlinks,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addResourceMetadata")
    def add_resource_metadata(
        self,
        resource: _CfnResource_e0a482dc,
        resource_property: builtins.str,
    ) -> None:
        '''(experimental) Adds CloudFormation template metadata to the specified resource with information that indicates which resource property is mapped to this local asset.

        This can be used by tools such as SAM CLI to provide local
        experience such as local invocation and debugging of Lambda functions.

        Asset metadata will only be included if the stack is synthesized with the
        "aws:cdk:enable-asset-metadata" context key defined, which is the default
        behavior when synthesizing via the CDK Toolkit.

        :param resource: The CloudFormation resource which is using this asset [disable-awslint:ref-via-interface].
        :param resource_property: The property name where this asset is referenced.

        :see: https://github.com/aws/aws-cdk/issues/1432
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addResourceMetadata", [resource, resource_property]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="assetHash")
    def asset_hash(self) -> builtins.str:
        '''(experimental) A hash of this asset, which is available at construction time.

        As this is a plain string, it
        can be used in construct IDs in order to enforce creation of a new resource when the content
        hash has changed.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "assetHash"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceHash")
    def source_hash(self) -> builtins.str:
        '''(deprecated) A hash of the source of this asset, which is available at construction time.

        As this is a plain
        string, it can be used in construct IDs in order to enforce creation of a new resource when
        the content hash has changed.

        :deprecated: use assetHash

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.get(self, "sourceHash"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageUri")
    def image_uri(self) -> builtins.str:
        '''(experimental) The full URI of the image (including a tag).

        Use this reference to pull
        the asset.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageUri"))

    @image_uri.setter
    def image_uri(self, value: builtins.str) -> None:
        jsii.set(self, "imageUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> _IRepository_8b4d2894:
        '''(experimental) Repository where the image is stored.

        :stability: experimental
        '''
        return typing.cast(_IRepository_8b4d2894, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: _IRepository_8b4d2894) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="monocdk.aws_ecr_assets.DockerImageAssetInvalidationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "build_args": "buildArgs",
        "extra_hash": "extraHash",
        "file": "file",
        "repository_name": "repositoryName",
        "target": "target",
    },
)
class DockerImageAssetInvalidationOptions:
    def __init__(
        self,
        *,
        build_args: typing.Optional[builtins.bool] = None,
        extra_hash: typing.Optional[builtins.bool] = None,
        file: typing.Optional[builtins.bool] = None,
        repository_name: typing.Optional[builtins.bool] = None,
        target: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options to control invalidation of ``DockerImageAsset`` asset hashes.

        :param build_args: (experimental) Use ``buildArgs`` while calculating the asset hash. Default: true
        :param extra_hash: (experimental) Use ``extraHash`` while calculating the asset hash. Default: true
        :param file: (experimental) Use ``file`` while calculating the asset hash. Default: true
        :param repository_name: (experimental) Use ``repositoryName`` while calculating the asset hash. Default: true
        :param target: (experimental) Use ``target`` while calculating the asset hash. Default: true

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from monocdk.aws_ecr_assets import DockerImageAsset
            
            
            asset = DockerImageAsset(self, "MyBuildImage",
                directory=path.join(__dirname, "my-image"),
                build_args={
                    "HTTP_PROXY": "http://10.20.30.2:1234"
                },
                invalidation=DockerImageAssetInvalidationOptions(
                    build_args=False
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if build_args is not None:
            self._values["build_args"] = build_args
        if extra_hash is not None:
            self._values["extra_hash"] = extra_hash
        if file is not None:
            self._values["file"] = file
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def build_args(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use ``buildArgs`` while calculating the asset hash.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("build_args")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def extra_hash(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use ``extraHash`` while calculating the asset hash.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("extra_hash")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def file(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use ``file`` while calculating the asset hash.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use ``repositoryName`` while calculating the asset hash.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use ``target`` while calculating the asset hash.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerImageAssetInvalidationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_ecr_assets.DockerImageAssetOptions",
    jsii_struct_bases=[_FingerprintOptions_2f2cdaa3, _FileFingerprintOptions_77e75a35],
    name_mapping={
        "exclude": "exclude",
        "follow": "follow",
        "ignore_mode": "ignoreMode",
        "extra_hash": "extraHash",
        "follow_symlinks": "followSymlinks",
        "build_args": "buildArgs",
        "file": "file",
        "invalidation": "invalidation",
        "repository_name": "repositoryName",
        "target": "target",
    },
)
class DockerImageAssetOptions(
    _FingerprintOptions_2f2cdaa3,
    _FileFingerprintOptions_77e75a35,
):
    def __init__(
        self,
        *,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow: typing.Optional[_FollowMode_98b05cc5] = None,
        ignore_mode: typing.Optional[_IgnoreMode_31d8bf46] = None,
        extra_hash: typing.Optional[builtins.str] = None,
        follow_symlinks: typing.Optional[_SymlinkFollowMode_abf4527a] = None,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        file: typing.Optional[builtins.str] = None,
        invalidation: typing.Optional[DockerImageAssetInvalidationOptions] = None,
        repository_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for DockerImageAsset.

        :param exclude: (experimental) Glob patterns to exclude from the copy. Default: - nothing is excluded
        :param follow: (deprecated) A strategy for how to handle symlinks. Default: Never
        :param ignore_mode: (experimental) The ignore behavior to use for exclude patterns. Default: IgnoreMode.GLOB
        :param extra_hash: (experimental) Extra information to encode into the fingerprint (e.g. build instructions and other inputs). Default: - hash is only based on source content
        :param follow_symlinks: (experimental) A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param build_args: (experimental) Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Default: - no build args are passed
        :param file: (experimental) Path to the Dockerfile (relative to the directory). Default: 'Dockerfile'
        :param invalidation: (experimental) Options to control which parameters are used to invalidate the asset hash. Default: - hash all parameters
        :param repository_name: (deprecated) ECR repository name. Specify this property if you need to statically address the image, e.g. from a Kubernetes Pod. Note, this is only the repository name, without the registry and the tag parts. Default: - the default ECR repository for CDK assets
        :param target: (experimental) Docker target to build to. Default: - no target

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import monocdk as monocdk
            from monocdk import assets
            from monocdk import aws_ecr_assets as ecr_assets
            
            docker_image_asset_options = ecr_assets.DockerImageAssetOptions(
                build_args={
                    "build_args_key": "buildArgs"
                },
                exclude=["exclude"],
                extra_hash="extraHash",
                file="file",
                follow=assets.FollowMode.NEVER,
                follow_symlinks=monocdk.SymlinkFollowMode.NEVER,
                ignore_mode=monocdk.IgnoreMode.GLOB,
                invalidation=ecr_assets.DockerImageAssetInvalidationOptions(
                    build_args=False,
                    extra_hash=False,
                    file=False,
                    repository_name=False,
                    target=False
                ),
                repository_name="repositoryName",
                target="target"
            )
        '''
        if isinstance(invalidation, dict):
            invalidation = DockerImageAssetInvalidationOptions(**invalidation)
        self._values: typing.Dict[str, typing.Any] = {}
        if exclude is not None:
            self._values["exclude"] = exclude
        if follow is not None:
            self._values["follow"] = follow
        if ignore_mode is not None:
            self._values["ignore_mode"] = ignore_mode
        if extra_hash is not None:
            self._values["extra_hash"] = extra_hash
        if follow_symlinks is not None:
            self._values["follow_symlinks"] = follow_symlinks
        if build_args is not None:
            self._values["build_args"] = build_args
        if file is not None:
            self._values["file"] = file
        if invalidation is not None:
            self._values["invalidation"] = invalidation
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Glob patterns to exclude from the copy.

        :default: - nothing is excluded

        :stability: experimental
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def follow(self) -> typing.Optional[_FollowMode_98b05cc5]:
        '''(deprecated) A strategy for how to handle symlinks.

        :default: Never

        :deprecated: use ``followSymlinks`` instead

        :stability: deprecated
        '''
        result = self._values.get("follow")
        return typing.cast(typing.Optional[_FollowMode_98b05cc5], result)

    @builtins.property
    def ignore_mode(self) -> typing.Optional[_IgnoreMode_31d8bf46]:
        '''(experimental) The ignore behavior to use for exclude patterns.

        :default: IgnoreMode.GLOB

        :stability: experimental
        '''
        result = self._values.get("ignore_mode")
        return typing.cast(typing.Optional[_IgnoreMode_31d8bf46], result)

    @builtins.property
    def extra_hash(self) -> typing.Optional[builtins.str]:
        '''(experimental) Extra information to encode into the fingerprint (e.g. build instructions and other inputs).

        :default: - hash is only based on source content

        :stability: experimental
        '''
        result = self._values.get("extra_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def follow_symlinks(self) -> typing.Optional[_SymlinkFollowMode_abf4527a]:
        '''(experimental) A strategy for how to handle symlinks.

        :default: SymlinkFollowMode.NEVER

        :stability: experimental
        '''
        result = self._values.get("follow_symlinks")
        return typing.cast(typing.Optional[_SymlinkFollowMode_abf4527a], result)

    @builtins.property
    def build_args(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Build args to pass to the ``docker build`` command.

        Since Docker build arguments are resolved before deployment, keys and
        values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or
        ``queue.queueUrl``).

        :default: - no build args are passed

        :stability: experimental
        '''
        result = self._values.get("build_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def file(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path to the Dockerfile (relative to the directory).

        :default: 'Dockerfile'

        :stability: experimental
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invalidation(self) -> typing.Optional[DockerImageAssetInvalidationOptions]:
        '''(experimental) Options to control which parameters are used to invalidate the asset hash.

        :default: - hash all parameters

        :stability: experimental
        '''
        result = self._values.get("invalidation")
        return typing.cast(typing.Optional[DockerImageAssetInvalidationOptions], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) ECR repository name.

        Specify this property if you need to statically address the image, e.g.
        from a Kubernetes Pod. Note, this is only the repository name, without the
        registry and the tag parts.

        :default: - the default ECR repository for CDK assets

        :deprecated:

        to control the location of docker image assets, please override
        ``Stack.addDockerImageAsset``. this feature will be removed in future
        releases.

        :stability: deprecated
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docker target to build to.

        :default: - no target

        :stability: experimental
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerImageAssetOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_ecr_assets.DockerImageAssetProps",
    jsii_struct_bases=[DockerImageAssetOptions],
    name_mapping={
        "exclude": "exclude",
        "follow": "follow",
        "ignore_mode": "ignoreMode",
        "extra_hash": "extraHash",
        "follow_symlinks": "followSymlinks",
        "build_args": "buildArgs",
        "file": "file",
        "invalidation": "invalidation",
        "repository_name": "repositoryName",
        "target": "target",
        "directory": "directory",
    },
)
class DockerImageAssetProps(DockerImageAssetOptions):
    def __init__(
        self,
        *,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow: typing.Optional[_FollowMode_98b05cc5] = None,
        ignore_mode: typing.Optional[_IgnoreMode_31d8bf46] = None,
        extra_hash: typing.Optional[builtins.str] = None,
        follow_symlinks: typing.Optional[_SymlinkFollowMode_abf4527a] = None,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        file: typing.Optional[builtins.str] = None,
        invalidation: typing.Optional[DockerImageAssetInvalidationOptions] = None,
        repository_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        directory: builtins.str,
    ) -> None:
        '''(experimental) Props for DockerImageAssets.

        :param exclude: (experimental) Glob patterns to exclude from the copy. Default: - nothing is excluded
        :param follow: (deprecated) A strategy for how to handle symlinks. Default: Never
        :param ignore_mode: (experimental) The ignore behavior to use for exclude patterns. Default: IgnoreMode.GLOB
        :param extra_hash: (experimental) Extra information to encode into the fingerprint (e.g. build instructions and other inputs). Default: - hash is only based on source content
        :param follow_symlinks: (experimental) A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param build_args: (experimental) Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Default: - no build args are passed
        :param file: (experimental) Path to the Dockerfile (relative to the directory). Default: 'Dockerfile'
        :param invalidation: (experimental) Options to control which parameters are used to invalidate the asset hash. Default: - hash all parameters
        :param repository_name: (deprecated) ECR repository name. Specify this property if you need to statically address the image, e.g. from a Kubernetes Pod. Note, this is only the repository name, without the registry and the tag parts. Default: - the default ECR repository for CDK assets
        :param target: (experimental) Docker target to build to. Default: - no target
        :param directory: (experimental) The directory where the Dockerfile is stored. Any directory inside with a name that matches the CDK output folder (cdk.out by default) will be excluded from the asset

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from monocdk.aws_ecr_assets import DockerImageAsset
            
            
            asset = DockerImageAsset(self, "MyBuildImage",
                directory=path.join(__dirname, "my-image"),
                build_args={
                    "HTTP_PROXY": "http://10.20.30.2:1234"
                },
                invalidation=DockerImageAssetInvalidationOptions(
                    build_args=False
                )
            )
        '''
        if isinstance(invalidation, dict):
            invalidation = DockerImageAssetInvalidationOptions(**invalidation)
        self._values: typing.Dict[str, typing.Any] = {
            "directory": directory,
        }
        if exclude is not None:
            self._values["exclude"] = exclude
        if follow is not None:
            self._values["follow"] = follow
        if ignore_mode is not None:
            self._values["ignore_mode"] = ignore_mode
        if extra_hash is not None:
            self._values["extra_hash"] = extra_hash
        if follow_symlinks is not None:
            self._values["follow_symlinks"] = follow_symlinks
        if build_args is not None:
            self._values["build_args"] = build_args
        if file is not None:
            self._values["file"] = file
        if invalidation is not None:
            self._values["invalidation"] = invalidation
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Glob patterns to exclude from the copy.

        :default: - nothing is excluded

        :stability: experimental
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def follow(self) -> typing.Optional[_FollowMode_98b05cc5]:
        '''(deprecated) A strategy for how to handle symlinks.

        :default: Never

        :deprecated: use ``followSymlinks`` instead

        :stability: deprecated
        '''
        result = self._values.get("follow")
        return typing.cast(typing.Optional[_FollowMode_98b05cc5], result)

    @builtins.property
    def ignore_mode(self) -> typing.Optional[_IgnoreMode_31d8bf46]:
        '''(experimental) The ignore behavior to use for exclude patterns.

        :default: IgnoreMode.GLOB

        :stability: experimental
        '''
        result = self._values.get("ignore_mode")
        return typing.cast(typing.Optional[_IgnoreMode_31d8bf46], result)

    @builtins.property
    def extra_hash(self) -> typing.Optional[builtins.str]:
        '''(experimental) Extra information to encode into the fingerprint (e.g. build instructions and other inputs).

        :default: - hash is only based on source content

        :stability: experimental
        '''
        result = self._values.get("extra_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def follow_symlinks(self) -> typing.Optional[_SymlinkFollowMode_abf4527a]:
        '''(experimental) A strategy for how to handle symlinks.

        :default: SymlinkFollowMode.NEVER

        :stability: experimental
        '''
        result = self._values.get("follow_symlinks")
        return typing.cast(typing.Optional[_SymlinkFollowMode_abf4527a], result)

    @builtins.property
    def build_args(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Build args to pass to the ``docker build`` command.

        Since Docker build arguments are resolved before deployment, keys and
        values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or
        ``queue.queueUrl``).

        :default: - no build args are passed

        :stability: experimental
        '''
        result = self._values.get("build_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def file(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path to the Dockerfile (relative to the directory).

        :default: 'Dockerfile'

        :stability: experimental
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invalidation(self) -> typing.Optional[DockerImageAssetInvalidationOptions]:
        '''(experimental) Options to control which parameters are used to invalidate the asset hash.

        :default: - hash all parameters

        :stability: experimental
        '''
        result = self._values.get("invalidation")
        return typing.cast(typing.Optional[DockerImageAssetInvalidationOptions], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) ECR repository name.

        Specify this property if you need to statically address the image, e.g.
        from a Kubernetes Pod. Note, this is only the repository name, without the
        registry and the tag parts.

        :default: - the default ECR repository for CDK assets

        :deprecated:

        to control the location of docker image assets, please override
        ``Stack.addDockerImageAsset``. this feature will be removed in future
        releases.

        :stability: deprecated
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docker target to build to.

        :default: - no target

        :stability: experimental
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def directory(self) -> builtins.str:
        '''(experimental) The directory where the Dockerfile is stored.

        Any directory inside with a name that matches the CDK output folder (cdk.out by default) will be excluded from the asset

        :stability: experimental
        '''
        result = self._values.get("directory")
        assert result is not None, "Required property 'directory' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerImageAssetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IAsset_092a7035)
class TarballImageAsset(
    _Construct_e78e779f,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_ecr_assets.TarballImageAsset",
):
    '''(experimental) An asset that represents a Docker image.

    The image will loaded from an existing tarball and uploaded to an ECR repository.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        from monocdk.aws_ecr_assets import TarballImageAsset
        
        
        asset = TarballImageAsset(self, "MyBuildImage",
            tarball_file="local-image.tar"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        tarball_file: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param tarball_file: (experimental) Absolute path to the tarball. It is recommended to to use the script running directory (e.g. ``__dirname`` in Node.js projects or dirname of ``__file__`` in Python) if your tarball is located as a resource inside your project.

        :stability: experimental
        '''
        props = TarballImageAssetProps(tarball_file=tarball_file)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="assetHash")
    def asset_hash(self) -> builtins.str:
        '''(experimental) A hash of this asset, which is available at construction time.

        As this is a plain string, it
        can be used in construct IDs in order to enforce creation of a new resource when the content
        hash has changed.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "assetHash"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceHash")
    def source_hash(self) -> builtins.str:
        '''(deprecated) A hash of the source of this asset, which is available at construction time.

        As this is a plain
        string, it can be used in construct IDs in order to enforce creation of a new resource when
        the content hash has changed.

        :deprecated: use assetHash

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.get(self, "sourceHash"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageUri")
    def image_uri(self) -> builtins.str:
        '''(experimental) The full URI of the image (including a tag).

        Use this reference to pull
        the asset.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageUri"))

    @image_uri.setter
    def image_uri(self, value: builtins.str) -> None:
        jsii.set(self, "imageUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repository")
    def repository(self) -> _IRepository_8b4d2894:
        '''(experimental) Repository where the image is stored.

        :stability: experimental
        '''
        return typing.cast(_IRepository_8b4d2894, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: _IRepository_8b4d2894) -> None:
        jsii.set(self, "repository", value)


@jsii.data_type(
    jsii_type="monocdk.aws_ecr_assets.TarballImageAssetProps",
    jsii_struct_bases=[],
    name_mapping={"tarball_file": "tarballFile"},
)
class TarballImageAssetProps:
    def __init__(self, *, tarball_file: builtins.str) -> None:
        '''(experimental) Options for TarballImageAsset.

        :param tarball_file: (experimental) Absolute path to the tarball. It is recommended to to use the script running directory (e.g. ``__dirname`` in Node.js projects or dirname of ``__file__`` in Python) if your tarball is located as a resource inside your project.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from monocdk.aws_ecr_assets import TarballImageAsset
            
            
            asset = TarballImageAsset(self, "MyBuildImage",
                tarball_file="local-image.tar"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "tarball_file": tarball_file,
        }

    @builtins.property
    def tarball_file(self) -> builtins.str:
        '''(experimental) Absolute path to the tarball.

        It is recommended to to use the script running directory (e.g. ``__dirname``
        in Node.js projects or dirname of ``__file__`` in Python) if your tarball
        is located as a resource inside your project.

        :stability: experimental
        '''
        result = self._values.get("tarball_file")
        assert result is not None, "Required property 'tarball_file' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TarballImageAssetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DockerImageAsset",
    "DockerImageAssetInvalidationOptions",
    "DockerImageAssetOptions",
    "DockerImageAssetProps",
    "TarballImageAsset",
    "TarballImageAssetProps",
]

publication.publish()
