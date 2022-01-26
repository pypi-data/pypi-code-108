'''
# Amazon Lambda Golang Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This library provides constructs for Golang Lambda functions.

To use this module you will either need to have `Go` installed (`go1.11` or later) or `Docker` installed.
See [Local Bundling](#local-bundling)/[Docker Bundling](#docker-bundling) for more information.

This module also requires that your Golang application is
using a Go version >= 1.11 and is using [Go modules](https://golang.org/ref/mod).

## Go Function

Define a `GoFunction`:

```python
lambda_.GoFunction(self, "handler",
    entry="app/cmd/api"
)
```

By default, if `entry` points to a directory, then the construct will assume there is a Go entry file (i.e. `main.go`).
Let's look at an example Go project:

```bash
lamda-app
├── cmd
│   └── api
│       └── main.go
├── go.mod
├── go.sum
├── pkg
│   ├── auth
│   │   └── auth.go
│   └── middleware
│       └── middleware.go
└── vendor
    ├── github.com
    │   └── aws
    │       └── aws-lambda-go
    └── modules.txt
```

With the above layout I could either provide the `entry` as `lambda-app/cmd/api` or `lambda-app/cmd/api/main.go`, either will work.
When the construct builds the golang binary this will be translated `go build ./cmd/api` & `go build ./cmd/api/main.go` respectively.
The construct will figure out where it needs to run the `go build` command from, in this example it would be from
the `lambda-app` directory. It does this by determining the [mod file path](#mod-file-path), which is explained in the
next section.

### mod file path

The `GoFunction` tries to automatically determine your project root, that is
the root of your golang project. This is usually where the top level `go.mod` file or
`vendor` folder of your project is located. When bundling in a Docker container, the
`moduleDir` is used as the source (`/asset-input`) for the volume mounted in
the container.

The CDK will walk up parent folders starting from
the current working directory until it finds a folder containing a `go.mod` file.

Alternatively, you can specify the `moduleDir` prop manually. In this case you
need to ensure that this path includes `entry` and any module/dependencies used
by your function. Otherwise bundling will fail.

## Runtime

The `GoFunction` can be used with either the `GO_1_X` runtime or the provided runtimes (`PROVIDED`/`PROVIDED_AL2`).
By default it will use the `PROVIDED_AL2` runtime. The `GO_1_X` runtime does not support things like
[Lambda Extensions](https://docs.aws.amazon.com/lambda/latest/dg/using-extensions.html), whereas the provided runtimes do.
The [aws-lambda-go](https://github.com/aws/aws-lambda-go) library has built in support for the provided runtime as long as
you name the handler `bootstrap` (which we do by default).

## Dependencies

The construct will attempt to figure out how to handle the dependencies for your function. It will
do this by determining whether or not you are vendoring your dependencies. It makes this determination
by looking to see if there is a `vendor` folder at the [mod file path](#mod-file-path).

With this information the construct can determine what commands to run. You will
generally fall into two scenarios:

1. You are using vendoring (indicated by the presence of a `vendor` folder)
   In this case `go build` will be run with `-mod=vendor` set
2. You are not using vendoring (indicated by the absence of a `vendor` folder)
   If you are not vendoring then `go build` will be run without `-mod=vendor`
   since the default behavior is to download dependencies

All other properties of `lambda.Function` are supported, see also the [AWS Lambda construct library](https://github.com/aws/aws-cdk/tree/master/packages/%40aws-cdk/aws-lambda).

## Environment

By default the following environment variables are set for you:

* `GOOS=linux`
* `GOARCH`: based on the target architecture of the Lambda function
* `GO111MODULE=on`

Use the `environment` prop to define additional environment variables when go runs:

```python
lambda_.GoFunction(self, "handler",
    entry="app/cmd/api",
    bundling=lambda.BundlingOptions(
        environment={
            "HELLO": "WORLD"
        }
    )
)
```

## Local Bundling

If `Go` is installed locally and the version is >= `go1.11` then it will be used to bundle your code in your environment. Otherwise, bundling will happen in a [Lambda compatible Docker container](https://gallery.ecr.aws/sam/build-go1.x) with the Docker platform based on the target architecture of the Lambda function.

For macOS the recommended approach is to install `Go` as Docker volume performance is really poor.

`Go` can be installed by following the [installation docs](https://golang.org/doc/install).

## Docker

To force bundling in a docker container even if `Go` is available in your environment, set the `forceDockerBundling` prop to `true`. This is useful if you want to make sure that your function is built in a consistent Lambda compatible environment.

Use the `buildArgs` prop to pass build arguments when building the bundling image:

```python
lambda_.GoFunction(self, "handler",
    entry="app/cmd/api",
    bundling=lambda.BundlingOptions(
        build_args={
            "HTTPS_PROXY": "https://127.0.0.1:3001"
        }
    )
)
```

Use the `bundling.dockerImage` prop to use a custom bundling image:

```python
lambda_.GoFunction(self, "handler",
    entry="app/cmd/api",
    bundling=lambda.BundlingOptions(
        docker_image=DockerImage.from_build("/path/to/Dockerfile")
    )
)
```

Use the `bundling.goBuildFlags` prop to pass additional build flags to `go build`:

```python
lambda_.GoFunction(self, "handler",
    entry="app/cmd/api",
    bundling=lambda.BundlingOptions(
        go_build_flags=["-ldflags \"-s -w\""]
    )
)
```

## Command hooks

It is  possible to run additional commands by specifying the `commandHooks` prop:

```text
// This example only available in TypeScript
// Run additional commands on a GoFunction via `commandHooks` property
new lambda.GoFunction(this, 'handler', {
  bundling: {
    commandHooks: {
      // run tests
      beforeBundling(inputDir: string): string[] {
        return ['go test ./cmd/api -v'];
      },
      // ...
    },
  },
});
```

The following hooks are available:

* `beforeBundling`: runs before all bundling commands
* `afterBundling`: runs after all bundling commands

They all receive the directory containing the `go.mod` file (`inputDir`) and the
directory where the bundled asset will be output (`outputDir`). They must return
an array of commands to run. Commands are chained with `&&`.

The commands will run in the environment in which bundling occurs: inside the
container for Docker bundling or on the host OS for local bundling.

## Additional considerations

Depending on how you structure your Golang application, you may want to change the `assetHashType` parameter.
By default this parameter is set to `AssetHashType.OUTPUT` which means that the CDK will calculate the asset hash
(and determine whether or not your code has changed) based on the Golang executable that is created.

If you specify `AssetHashType.SOURCE`, the CDK will calculate the asset hash by looking at the folder
that contains your `go.mod` file. If you are deploying a single Lambda function, or you want to redeploy
all of your functions if anything changes, then `AssetHashType.SOURCE` will probaby work.

For example, if my app looked like this:

```bash
lamda-app
├── cmd
│   └── api
│       └── main.go
├── go.mod
├── go.sum
└── pkg
    └── auth
        └── auth.go
```

With this structure I would provide the `entry` as `cmd/api` which means that the CDK
will determine that the protect root is `lambda-app` (it contains the `go.mod` file).
Since I only have a single Lambda function, and any update to files within the `lambda-app` directory
should trigger a new deploy, I could specify `AssetHashType.SOURCE`.

On the other hand, if I had a project that deployed mmultiple Lambda functions, for example:

```bash
lamda-app
├── cmd
│   ├── api
│   │   └── main.go
│   └── anotherApi
│       └── main.go
├── go.mod
├── go.sum
└── pkg
    ├── auth
    │   └── auth.go
    └── middleware
        └── middleware.go
```

Then I would most likely want `AssetHashType.OUTPUT`. With `OUTPUT`
the CDK will only recognize changes if the Golang executable has changed,
and Go only includes dependencies that are used in the executable. So in this case
if `cmd/api` used the `auth` & `middleware` packages, but `cmd/anotherApi` did not, then
an update to `auth` or `middleware` would only trigger an update to the `cmd/api` Lambda
Function.
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

import aws_cdk
import aws_cdk.aws_codeguruprofiler
import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.aws_sqs
import constructs


@jsii.data_type(
    jsii_type="@aws-cdk/aws-lambda-go-alpha.BundlingOptions",
    jsii_struct_bases=[],
    name_mapping={
        "asset_hash": "assetHash",
        "asset_hash_type": "assetHashType",
        "build_args": "buildArgs",
        "cgo_enabled": "cgoEnabled",
        "command_hooks": "commandHooks",
        "docker_image": "dockerImage",
        "environment": "environment",
        "forced_docker_bundling": "forcedDockerBundling",
        "go_build_flags": "goBuildFlags",
    },
)
class BundlingOptions:
    def __init__(
        self,
        *,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[aws_cdk.AssetHashType] = None,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        cgo_enabled: typing.Optional[builtins.bool] = None,
        command_hooks: typing.Optional["ICommandHooks"] = None,
        docker_image: typing.Optional[aws_cdk.DockerImage] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        forced_docker_bundling: typing.Optional[builtins.bool] = None,
        go_build_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Bundling options.

        :param asset_hash: (experimental) Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: (experimental) Determines how the asset hash is calculated. Assets will get rebuilt and uploaded only if their hash has changed. If the asset hash is set to ``OUTPUT`` (default), the hash is calculated after bundling. This means that any change in the output will cause the asset to be invalidated and uploaded. Bear in mind that the go binary that is output can be different depending on the environment that it was compiled in. If you want to control when the output is changed it is recommended that you use immutable build images such as ``public.ecr.aws/bitnami/golang:1.16.3-debian-10-r16``. If the asset hash is set to ``SOURCE``, then only changes to the source directory will cause the asset to rebuild. If your go project has multiple Lambda functions this means that an update to any one function could cause all the functions to be rebuilt and uploaded. Default: - AssetHashType.OUTPUT. If ``assetHash`` is also specified, the default is ``CUSTOM``.
        :param build_args: (experimental) Build arguments to pass when building the bundling image. Default: - no build arguments are passed
        :param cgo_enabled: (experimental) Whether or not to enable cgo during go build. This will set the CGO_ENABLED environment variable Default: - false
        :param command_hooks: (experimental) Command hooks. Default: - do not run additional commands
        :param docker_image: (experimental) A custom bundling Docker image. Default: - use the Docker image provided by
        :param environment: (experimental) Environment variables defined when go runs. Default: - no environment variables are defined.
        :param forced_docker_bundling: (experimental) Force bundling in a Docker container even if local bundling is possible. Default: - false
        :param go_build_flags: (experimental) List of additional flags to use while building. For example: ['ldflags "-s -w"'] Default: - none

        :stability: experimental
        :exampleMetadata: infused

        Example::

            lambda_.GoFunction(self, "handler",
                entry="app/cmd/api",
                bundling=lambda.BundlingOptions(
                    environment={
                        "HELLO": "WORLD"
                    }
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if asset_hash is not None:
            self._values["asset_hash"] = asset_hash
        if asset_hash_type is not None:
            self._values["asset_hash_type"] = asset_hash_type
        if build_args is not None:
            self._values["build_args"] = build_args
        if cgo_enabled is not None:
            self._values["cgo_enabled"] = cgo_enabled
        if command_hooks is not None:
            self._values["command_hooks"] = command_hooks
        if docker_image is not None:
            self._values["docker_image"] = docker_image
        if environment is not None:
            self._values["environment"] = environment
        if forced_docker_bundling is not None:
            self._values["forced_docker_bundling"] = forced_docker_bundling
        if go_build_flags is not None:
            self._values["go_build_flags"] = go_build_flags

    @builtins.property
    def asset_hash(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specify a custom hash for this asset.

        If ``assetHashType`` is set it must
        be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will
        be SHA256 hashed and encoded as hex. The resulting hash will be the asset
        hash.

        NOTE: the hash is used in order to identify a specific revision of the asset, and
        used for optimizing and caching deployment activities related to this asset such as
        packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will
        need to make sure it is updated every time the asset changes, or otherwise it is
        possible that some deployments will not be invalidated.

        :default: - based on ``assetHashType``

        :stability: experimental
        '''
        result = self._values.get("asset_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_hash_type(self) -> typing.Optional[aws_cdk.AssetHashType]:
        '''(experimental) Determines how the asset hash is calculated. Assets will get rebuilt and uploaded only if their hash has changed.

        If the asset hash is set to ``OUTPUT`` (default), the hash is calculated
        after bundling. This means that any change in the output will cause
        the asset to be invalidated and uploaded. Bear in mind that the
        go binary that is output can be different depending on the environment
        that it was compiled in. If you want to control when the output is changed
        it is recommended that you use immutable build images such as
        ``public.ecr.aws/bitnami/golang:1.16.3-debian-10-r16``.

        If the asset hash is set to ``SOURCE``, then only changes to the source
        directory will cause the asset to rebuild. If your go project has multiple
        Lambda functions this means that an update to any one function could cause
        all the functions to be rebuilt and uploaded.

        :default:

        - AssetHashType.OUTPUT. If ``assetHash`` is also specified,
        the default is ``CUSTOM``.

        :stability: experimental
        '''
        result = self._values.get("asset_hash_type")
        return typing.cast(typing.Optional[aws_cdk.AssetHashType], result)

    @builtins.property
    def build_args(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Build arguments to pass when building the bundling image.

        :default: - no build arguments are passed

        :stability: experimental
        '''
        result = self._values.get("build_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def cgo_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not to enable cgo during go build.

        This will set the CGO_ENABLED environment variable

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("cgo_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def command_hooks(self) -> typing.Optional["ICommandHooks"]:
        '''(experimental) Command hooks.

        :default: - do not run additional commands

        :stability: experimental
        '''
        result = self._values.get("command_hooks")
        return typing.cast(typing.Optional["ICommandHooks"], result)

    @builtins.property
    def docker_image(self) -> typing.Optional[aws_cdk.DockerImage]:
        '''(experimental) A custom bundling Docker image.

        :default: - use the Docker image provided by

        :stability: experimental
        :aws-cdk: /aws-lambda-go
        '''
        result = self._values.get("docker_image")
        return typing.cast(typing.Optional[aws_cdk.DockerImage], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables defined when go runs.

        :default: - no environment variables are defined.

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def forced_docker_bundling(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Force bundling in a Docker container even if local bundling is possible.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("forced_docker_bundling")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def go_build_flags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of additional flags to use while building.

        For example:
        ['ldflags "-s -w"']

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("go_build_flags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BundlingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GoFunction(
    aws_cdk.aws_lambda.Function,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-lambda-go-alpha.GoFunction",
):
    '''(experimental) A Golang Lambda function.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        lambda_.GoFunction(self, "handler",
            entry="app/cmd/api",
            bundling=lambda.BundlingOptions(
                go_build_flags=["-ldflags \"-s -w\""]
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        entry: builtins.str,
        bundling: typing.Optional[BundlingOptions] = None,
        module_dir: typing.Optional[builtins.str] = None,
        runtime: typing.Optional[aws_cdk.aws_lambda.Runtime] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        allow_public_subnet: typing.Optional[builtins.bool] = None,
        architecture: typing.Optional[aws_cdk.aws_lambda.Architecture] = None,
        code_signing_config: typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig] = None,
        current_version_options: typing.Optional[aws_cdk.aws_lambda.VersionOptions] = None,
        dead_letter_queue: typing.Optional[aws_cdk.aws_sqs.IQueue] = None,
        dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment_encryption: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        events: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.IEventSource]] = None,
        filesystem: typing.Optional[aws_cdk.aws_lambda.FileSystem] = None,
        function_name: typing.Optional[builtins.str] = None,
        initial_policy: typing.Optional[typing.Sequence[aws_cdk.aws_iam.PolicyStatement]] = None,
        insights_version: typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion] = None,
        layers: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.ILayerVersion]] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        log_retention_retry_options: typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions] = None,
        log_retention_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        profiling: typing.Optional[builtins.bool] = None,
        profiling_group: typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
        tracing: typing.Optional[aws_cdk.aws_lambda.Tracing] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        max_event_age: typing.Optional[aws_cdk.Duration] = None,
        on_failure: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_success: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param entry: (experimental) The path to the folder or file that contains the main application entry point files for the project. This accepts either a path to a directory or file. If a directory path is provided then it will assume there is a Go entry file (i.e. ``main.go``) and will construct the build command using the directory path. For example, if you provide the entry as:: entry: 'my-lambda-app/cmd/api' Then the ``go build`` command would be:: `go build ./cmd/api` If a path to a file is provided then it will use the filepath in the build command. For example, if you provide the entry as:: entry: 'my-lambda-app/cmd/api/main.go' Then the ``go build`` command would be:: `go build ./cmd/api/main.go`
        :param bundling: (experimental) Bundling options. Default: - use default bundling options
        :param module_dir: (experimental) Directory containing your go.mod file. This will accept either a directory path containing a ``go.mod`` file or a filepath to your ``go.mod`` file (i.e. ``path/to/go.mod``). This will be used as the source of the volume mounted in the Docker container and will be the directory where it will run ``go build`` from. Default: - the path is found by walking up parent directories searching for a ``go.mod`` file from the location of ``entry``
        :param runtime: (experimental) The runtime environment. Only runtimes of the Golang family and provided family are supported. Default: lambda.Runtime.PROVIDED_AL2
        :param allow_all_outbound: Whether to allow the Lambda to send all network traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Default: true
        :param allow_public_subnet: Lambda Functions in a public subnet can NOT access the internet. Use this property to acknowledge this limitation and still place the function in a public subnet. Default: false
        :param architecture: The system architectures compatible with this lambda function. Default: Architecture.X86_64
        :param code_signing_config: Code signing config associated with this function. Default: - Not Sign the Code
        :param current_version_options: Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method. Default: - default options as described in ``VersionOptions``
        :param dead_letter_queue: The SQS queue to use if DLQ is enabled. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        :param dead_letter_queue_enabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        :param description: A description of the function. Default: - No description.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
        :param environment_encryption: The AWS KMS key that's used to encrypt your function's environment variables. Default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        :param events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
        :param filesystem: The filesystem configuration for the lambda function. Default: - will not mount any filesystem
        :param function_name: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
        :param initial_policy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
        :param insights_version: Specify the version of CloudWatch Lambda insights to use for monitoring. Default: - No Lambda Insights
        :param layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by multiple functions. Default: - No layers.
        :param log_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.INFINITE
        :param log_retention_retry_options: When log retention is specified, a custom resource attempts to create the CloudWatch log group. These options control the retry policy when interacting with CloudWatch APIs. Default: - Default AWS SDK retry options.
        :param log_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - A new role is created.
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
        :param profiling: Enable profiling. Default: - No profiling.
        :param profiling_group: Profiling Group. Default: - A new profiling group will be created if ``profiling`` is set.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
        :param role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. The default Role automatically has permissions granted for Lambda execution. If you provide a Role, you must add the relevant AWS managed policies yourself. The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and "service-role/AWSLambdaVPCAccessExecutionRole". Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        :param security_groups: The list of security groups to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroup prop, a dedicated security group will be created for this function.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(3)
        :param tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
        :param vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. Default: - Function is not placed within a VPC.
        :param vpc_subnets: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Note: internet access for Lambdas requires a NAT gateway, so picking Public subnets is not allowed. Default: - the Vpc default strategy if not specified
        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum: 60 seconds Maximum: 6 hours Default: Duration.hours(6)
        :param on_failure: The destination for failed invocations. Default: - no destination
        :param on_success: The destination for successful invocations. Default: - no destination
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum: 0 Maximum: 2 Default: 2

        :stability: experimental
        '''
        props = GoFunctionProps(
            entry=entry,
            bundling=bundling,
            module_dir=module_dir,
            runtime=runtime,
            allow_all_outbound=allow_all_outbound,
            allow_public_subnet=allow_public_subnet,
            architecture=architecture,
            code_signing_config=code_signing_config,
            current_version_options=current_version_options,
            dead_letter_queue=dead_letter_queue,
            dead_letter_queue_enabled=dead_letter_queue_enabled,
            description=description,
            environment=environment,
            environment_encryption=environment_encryption,
            events=events,
            filesystem=filesystem,
            function_name=function_name,
            initial_policy=initial_policy,
            insights_version=insights_version,
            layers=layers,
            log_retention=log_retention,
            log_retention_retry_options=log_retention_retry_options,
            log_retention_role=log_retention_role,
            memory_size=memory_size,
            profiling=profiling,
            profiling_group=profiling_group,
            reserved_concurrent_executions=reserved_concurrent_executions,
            role=role,
            security_groups=security_groups,
            timeout=timeout,
            tracing=tracing,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            max_event_age=max_event_age,
            on_failure=on_failure,
            on_success=on_success,
            retry_attempts=retry_attempts,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-lambda-go-alpha.GoFunctionProps",
    jsii_struct_bases=[aws_cdk.aws_lambda.FunctionOptions],
    name_mapping={
        "max_event_age": "maxEventAge",
        "on_failure": "onFailure",
        "on_success": "onSuccess",
        "retry_attempts": "retryAttempts",
        "allow_all_outbound": "allowAllOutbound",
        "allow_public_subnet": "allowPublicSubnet",
        "architecture": "architecture",
        "code_signing_config": "codeSigningConfig",
        "current_version_options": "currentVersionOptions",
        "dead_letter_queue": "deadLetterQueue",
        "dead_letter_queue_enabled": "deadLetterQueueEnabled",
        "description": "description",
        "environment": "environment",
        "environment_encryption": "environmentEncryption",
        "events": "events",
        "filesystem": "filesystem",
        "function_name": "functionName",
        "initial_policy": "initialPolicy",
        "insights_version": "insightsVersion",
        "layers": "layers",
        "log_retention": "logRetention",
        "log_retention_retry_options": "logRetentionRetryOptions",
        "log_retention_role": "logRetentionRole",
        "memory_size": "memorySize",
        "profiling": "profiling",
        "profiling_group": "profilingGroup",
        "reserved_concurrent_executions": "reservedConcurrentExecutions",
        "role": "role",
        "security_groups": "securityGroups",
        "timeout": "timeout",
        "tracing": "tracing",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "entry": "entry",
        "bundling": "bundling",
        "module_dir": "moduleDir",
        "runtime": "runtime",
    },
)
class GoFunctionProps(aws_cdk.aws_lambda.FunctionOptions):
    def __init__(
        self,
        *,
        max_event_age: typing.Optional[aws_cdk.Duration] = None,
        on_failure: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_success: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        allow_public_subnet: typing.Optional[builtins.bool] = None,
        architecture: typing.Optional[aws_cdk.aws_lambda.Architecture] = None,
        code_signing_config: typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig] = None,
        current_version_options: typing.Optional[aws_cdk.aws_lambda.VersionOptions] = None,
        dead_letter_queue: typing.Optional[aws_cdk.aws_sqs.IQueue] = None,
        dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment_encryption: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        events: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.IEventSource]] = None,
        filesystem: typing.Optional[aws_cdk.aws_lambda.FileSystem] = None,
        function_name: typing.Optional[builtins.str] = None,
        initial_policy: typing.Optional[typing.Sequence[aws_cdk.aws_iam.PolicyStatement]] = None,
        insights_version: typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion] = None,
        layers: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.ILayerVersion]] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        log_retention_retry_options: typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions] = None,
        log_retention_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        profiling: typing.Optional[builtins.bool] = None,
        profiling_group: typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
        tracing: typing.Optional[aws_cdk.aws_lambda.Tracing] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        entry: builtins.str,
        bundling: typing.Optional[BundlingOptions] = None,
        module_dir: typing.Optional[builtins.str] = None,
        runtime: typing.Optional[aws_cdk.aws_lambda.Runtime] = None,
    ) -> None:
        '''(experimental) Properties for a GolangFunction.

        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum: 60 seconds Maximum: 6 hours Default: Duration.hours(6)
        :param on_failure: The destination for failed invocations. Default: - no destination
        :param on_success: The destination for successful invocations. Default: - no destination
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum: 0 Maximum: 2 Default: 2
        :param allow_all_outbound: Whether to allow the Lambda to send all network traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Default: true
        :param allow_public_subnet: Lambda Functions in a public subnet can NOT access the internet. Use this property to acknowledge this limitation and still place the function in a public subnet. Default: false
        :param architecture: The system architectures compatible with this lambda function. Default: Architecture.X86_64
        :param code_signing_config: Code signing config associated with this function. Default: - Not Sign the Code
        :param current_version_options: Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method. Default: - default options as described in ``VersionOptions``
        :param dead_letter_queue: The SQS queue to use if DLQ is enabled. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        :param dead_letter_queue_enabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        :param description: A description of the function. Default: - No description.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
        :param environment_encryption: The AWS KMS key that's used to encrypt your function's environment variables. Default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        :param events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
        :param filesystem: The filesystem configuration for the lambda function. Default: - will not mount any filesystem
        :param function_name: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
        :param initial_policy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
        :param insights_version: Specify the version of CloudWatch Lambda insights to use for monitoring. Default: - No Lambda Insights
        :param layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by multiple functions. Default: - No layers.
        :param log_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.INFINITE
        :param log_retention_retry_options: When log retention is specified, a custom resource attempts to create the CloudWatch log group. These options control the retry policy when interacting with CloudWatch APIs. Default: - Default AWS SDK retry options.
        :param log_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - A new role is created.
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
        :param profiling: Enable profiling. Default: - No profiling.
        :param profiling_group: Profiling Group. Default: - A new profiling group will be created if ``profiling`` is set.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
        :param role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. The default Role automatically has permissions granted for Lambda execution. If you provide a Role, you must add the relevant AWS managed policies yourself. The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and "service-role/AWSLambdaVPCAccessExecutionRole". Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        :param security_groups: The list of security groups to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroup prop, a dedicated security group will be created for this function.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(3)
        :param tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
        :param vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. Default: - Function is not placed within a VPC.
        :param vpc_subnets: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Note: internet access for Lambdas requires a NAT gateway, so picking Public subnets is not allowed. Default: - the Vpc default strategy if not specified
        :param entry: (experimental) The path to the folder or file that contains the main application entry point files for the project. This accepts either a path to a directory or file. If a directory path is provided then it will assume there is a Go entry file (i.e. ``main.go``) and will construct the build command using the directory path. For example, if you provide the entry as:: entry: 'my-lambda-app/cmd/api' Then the ``go build`` command would be:: `go build ./cmd/api` If a path to a file is provided then it will use the filepath in the build command. For example, if you provide the entry as:: entry: 'my-lambda-app/cmd/api/main.go' Then the ``go build`` command would be:: `go build ./cmd/api/main.go`
        :param bundling: (experimental) Bundling options. Default: - use default bundling options
        :param module_dir: (experimental) Directory containing your go.mod file. This will accept either a directory path containing a ``go.mod`` file or a filepath to your ``go.mod`` file (i.e. ``path/to/go.mod``). This will be used as the source of the volume mounted in the Docker container and will be the directory where it will run ``go build`` from. Default: - the path is found by walking up parent directories searching for a ``go.mod`` file from the location of ``entry``
        :param runtime: (experimental) The runtime environment. Only runtimes of the Golang family and provided family are supported. Default: lambda.Runtime.PROVIDED_AL2

        :stability: experimental
        :exampleMetadata: infused

        Example::

            lambda_.GoFunction(self, "handler",
                entry="app/cmd/api",
                bundling=lambda.BundlingOptions(
                    go_build_flags=["-ldflags \"-s -w\""]
                )
            )
        '''
        if isinstance(current_version_options, dict):
            current_version_options = aws_cdk.aws_lambda.VersionOptions(**current_version_options)
        if isinstance(log_retention_retry_options, dict):
            log_retention_retry_options = aws_cdk.aws_lambda.LogRetentionRetryOptions(**log_retention_retry_options)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        if isinstance(bundling, dict):
            bundling = BundlingOptions(**bundling)
        self._values: typing.Dict[str, typing.Any] = {
            "entry": entry,
        }
        if max_event_age is not None:
            self._values["max_event_age"] = max_event_age
        if on_failure is not None:
            self._values["on_failure"] = on_failure
        if on_success is not None:
            self._values["on_success"] = on_success
        if retry_attempts is not None:
            self._values["retry_attempts"] = retry_attempts
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if allow_public_subnet is not None:
            self._values["allow_public_subnet"] = allow_public_subnet
        if architecture is not None:
            self._values["architecture"] = architecture
        if code_signing_config is not None:
            self._values["code_signing_config"] = code_signing_config
        if current_version_options is not None:
            self._values["current_version_options"] = current_version_options
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if dead_letter_queue_enabled is not None:
            self._values["dead_letter_queue_enabled"] = dead_letter_queue_enabled
        if description is not None:
            self._values["description"] = description
        if environment is not None:
            self._values["environment"] = environment
        if environment_encryption is not None:
            self._values["environment_encryption"] = environment_encryption
        if events is not None:
            self._values["events"] = events
        if filesystem is not None:
            self._values["filesystem"] = filesystem
        if function_name is not None:
            self._values["function_name"] = function_name
        if initial_policy is not None:
            self._values["initial_policy"] = initial_policy
        if insights_version is not None:
            self._values["insights_version"] = insights_version
        if layers is not None:
            self._values["layers"] = layers
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if log_retention_retry_options is not None:
            self._values["log_retention_retry_options"] = log_retention_retry_options
        if log_retention_role is not None:
            self._values["log_retention_role"] = log_retention_role
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if profiling is not None:
            self._values["profiling"] = profiling
        if profiling_group is not None:
            self._values["profiling_group"] = profiling_group
        if reserved_concurrent_executions is not None:
            self._values["reserved_concurrent_executions"] = reserved_concurrent_executions
        if role is not None:
            self._values["role"] = role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if timeout is not None:
            self._values["timeout"] = timeout
        if tracing is not None:
            self._values["tracing"] = tracing
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if bundling is not None:
            self._values["bundling"] = bundling
        if module_dir is not None:
            self._values["module_dir"] = module_dir
        if runtime is not None:
            self._values["runtime"] = runtime

    @builtins.property
    def max_event_age(self) -> typing.Optional[aws_cdk.Duration]:
        '''The maximum age of a request that Lambda sends to a function for processing.

        Minimum: 60 seconds
        Maximum: 6 hours

        :default: Duration.hours(6)
        '''
        result = self._values.get("max_event_age")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def on_failure(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        '''The destination for failed invocations.

        :default: - no destination
        '''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    @builtins.property
    def on_success(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        '''The destination for successful invocations.

        :default: - no destination
        '''
        result = self._values.get("on_success")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    @builtins.property
    def retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times to retry when the function returns an error.

        Minimum: 0
        Maximum: 2

        :default: 2
        '''
        result = self._values.get("retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the Lambda to send all network traffic.

        If set to false, you must individually add traffic rules to allow the
        Lambda to connect to network targets.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_public_subnet(self) -> typing.Optional[builtins.bool]:
        '''Lambda Functions in a public subnet can NOT access the internet.

        Use this property to acknowledge this limitation and still place the function in a public subnet.

        :default: false

        :see: https://stackoverflow.com/questions/52992085/why-cant-an-aws-lambda-function-inside-a-public-subnet-in-a-vpc-connect-to-the/52994841#52994841
        '''
        result = self._values.get("allow_public_subnet")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def architecture(self) -> typing.Optional[aws_cdk.aws_lambda.Architecture]:
        '''The system architectures compatible with this lambda function.

        :default: Architecture.X86_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Architecture], result)

    @builtins.property
    def code_signing_config(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig]:
        '''Code signing config associated with this function.

        :default: - Not Sign the Code
        '''
        result = self._values.get("code_signing_config")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig], result)

    @builtins.property
    def current_version_options(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.VersionOptions]:
        '''Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method.

        :default: - default options as described in ``VersionOptions``
        '''
        result = self._values.get("current_version_options")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.VersionOptions], result)

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[aws_cdk.aws_sqs.IQueue]:
        '''The SQS queue to use if DLQ is enabled.

        :default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.IQueue], result)

    @builtins.property
    def dead_letter_queue_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enabled DLQ.

        If ``deadLetterQueue`` is undefined,
        an SQS queue with default options will be defined for your Function.

        :default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        '''
        result = self._values.get("dead_letter_queue_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the function.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Key-value pairs that Lambda caches and makes available for your Lambda functions.

        Use environment variables to apply configuration changes, such
        as test and production environment configurations, without changing your
        Lambda function source code.

        :default: - No environment variables.
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def environment_encryption(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''The AWS KMS key that's used to encrypt your function's environment variables.

        :default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        '''
        result = self._values.get("environment_encryption")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def events(self) -> typing.Optional[typing.List[aws_cdk.aws_lambda.IEventSource]]:
        '''Event sources for this function.

        You can also add event sources using ``addEventSource``.

        :default: - No event sources.
        '''
        result = self._values.get("events")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_lambda.IEventSource]], result)

    @builtins.property
    def filesystem(self) -> typing.Optional[aws_cdk.aws_lambda.FileSystem]:
        '''The filesystem configuration for the lambda function.

        :default: - will not mount any filesystem
        '''
        result = self._values.get("filesystem")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FileSystem], result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''A name for the function.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that
        ID for the function's name. For more information, see Name Type.
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def initial_policy(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]]:
        '''Initial policy statements to add to the created Lambda Role.

        You can call ``addToRolePolicy`` to the created lambda to add statements post creation.

        :default: - No policy statements are added to the created Lambda role.
        '''
        result = self._values.get("initial_policy")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]], result)

    @builtins.property
    def insights_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion]:
        '''Specify the version of CloudWatch Lambda insights to use for monitoring.

        :default: - No Lambda Insights

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Lambda-Insights-Getting-Started-docker.html
        '''
        result = self._values.get("insights_version")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion], result)

    @builtins.property
    def layers(self) -> typing.Optional[typing.List[aws_cdk.aws_lambda.ILayerVersion]]:
        '''A list of layers to add to the function's execution environment.

        You can configure your Lambda function to pull in
        additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies
        that can be used by multiple functions.

        :default: - No layers.
        '''
        result = self._values.get("layers")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_lambda.ILayerVersion]], result)

    @builtins.property
    def log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``INFINITE``.

        :default: logs.RetentionDays.INFINITE
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def log_retention_retry_options(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions]:
        '''When log retention is specified, a custom resource attempts to create the CloudWatch log group.

        These options control the retry policy when interacting with CloudWatch APIs.

        :default: - Default AWS SDK retry options.
        '''
        result = self._values.get("log_retention_retry_options")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions], result)

    @builtins.property
    def log_retention_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

        :default: - A new role is created.
        '''
        result = self._values.get("log_retention_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory, in MB, that is allocated to your Lambda function.

        Lambda uses this value to proportionally allocate the amount of CPU
        power. For more information, see Resource Model in the AWS Lambda
        Developer Guide.

        :default: 128
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def profiling(self) -> typing.Optional[builtins.bool]:
        '''Enable profiling.

        :default: - No profiling.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profiling_group(
        self,
    ) -> typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup]:
        '''Profiling Group.

        :default: - A new profiling group will be created if ``profiling`` is set.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling_group")
        return typing.cast(typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup], result)

    @builtins.property
    def reserved_concurrent_executions(self) -> typing.Optional[jsii.Number]:
        '''The maximum of concurrent executions you want to reserve for the function.

        :default: - No specific limit - account limit.

        :see: https://docs.aws.amazon.com/lambda/latest/dg/concurrent-executions.html
        '''
        result = self._values.get("reserved_concurrent_executions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Lambda execution role.

        This is the role that will be assumed by the function upon execution.
        It controls the permissions that the function will have. The Role must
        be assumable by the 'lambda.amazonaws.com' service principal.

        The default Role automatically has permissions granted for Lambda execution. If you
        provide a Role, you must add the relevant AWS managed policies yourself.

        The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and
        "service-role/AWSLambdaVPCAccessExecutionRole".

        :default:

        - A unique role will be generated for this lambda function.
        Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        '''The list of security groups to associate with the Lambda's network interfaces.

        Only used if 'vpc' is supplied.

        :default:

        - If the function is placed within a VPC and a security group is
        not specified, either by this or securityGroup prop, a dedicated security
        group will be created for this function.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value
        based on the function's expected execution time.

        :default: Duration.seconds(3)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def tracing(self) -> typing.Optional[aws_cdk.aws_lambda.Tracing]:
        '''Enable AWS X-Ray Tracing for Lambda Function.

        :default: Tracing.Disabled
        '''
        result = self._values.get("tracing")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Tracing], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC network to place Lambda network interfaces.

        Specify this if the Lambda function needs to access resources in a VPC.

        :default: - Function is not placed within a VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.

        Only used if 'vpc' is supplied. Note: internet access for Lambdas
        requires a NAT gateway, so picking Public subnets is not allowed.

        :default: - the Vpc default strategy if not specified
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def entry(self) -> builtins.str:
        '''(experimental) The path to the folder or file that contains the main application entry point files for the project.

        This accepts either a path to a directory or file.

        If a directory path is provided then it will assume there is a Go entry file (i.e. ``main.go``) and
        will construct the build command using the directory path.

        For example, if you provide the entry as::

            entry: 'my-lambda-app/cmd/api'

        Then the ``go build`` command would be::

            `go build ./cmd/api`

        If a path to a file is provided then it will use the filepath in the build command.

        For example, if you provide the entry as::

            entry: 'my-lambda-app/cmd/api/main.go'

        Then the ``go build`` command would be::

            `go build ./cmd/api/main.go`

        :stability: experimental
        '''
        result = self._values.get("entry")
        assert result is not None, "Required property 'entry' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bundling(self) -> typing.Optional[BundlingOptions]:
        '''(experimental) Bundling options.

        :default: - use default bundling options

        :stability: experimental
        '''
        result = self._values.get("bundling")
        return typing.cast(typing.Optional[BundlingOptions], result)

    @builtins.property
    def module_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Directory containing your go.mod file.

        This will accept either a directory path containing a ``go.mod`` file
        or a filepath to your ``go.mod`` file (i.e. ``path/to/go.mod``).

        This will be used as the source of the volume mounted in the Docker
        container and will be the directory where it will run ``go build`` from.

        :default:

        - the path is found by walking up parent directories searching for
        a ``go.mod`` file from the location of ``entry``

        :stability: experimental
        '''
        result = self._values.get("module_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runtime(self) -> typing.Optional[aws_cdk.aws_lambda.Runtime]:
        '''(experimental) The runtime environment.

        Only runtimes of the Golang family and provided family are supported.

        :default: lambda.Runtime.PROVIDED_AL2

        :stability: experimental
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Runtime], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-lambda-go-alpha.ICommandHooks")
class ICommandHooks(typing_extensions.Protocol):
    '''(experimental) Command hooks.

    These commands will run in the environment in which bundling occurs: inside
    the container for Docker bundling or on the host OS for local bundling.

    Commands are chained with ``&&``::

       {
          // Run tests prior to bundling
          beforeBundling(inputDir: string, outputDir: string): string[] {
            return [`go test -mod=vendor ./...`];
          }
          // ...
       }

    :stability: experimental
    '''

    @jsii.member(jsii_name="afterBundling")
    def after_bundling(
        self,
        input_dir: builtins.str,
        output_dir: builtins.str,
    ) -> typing.List[builtins.str]:
        '''(experimental) Returns commands to run after bundling.

        Commands are chained with ``&&``.

        :param input_dir: -
        :param output_dir: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="beforeBundling")
    def before_bundling(
        self,
        input_dir: builtins.str,
        output_dir: builtins.str,
    ) -> typing.List[builtins.str]:
        '''(experimental) Returns commands to run before bundling.

        Commands are chained with ``&&``.

        :param input_dir: -
        :param output_dir: -

        :stability: experimental
        '''
        ...


class _ICommandHooksProxy:
    '''(experimental) Command hooks.

    These commands will run in the environment in which bundling occurs: inside
    the container for Docker bundling or on the host OS for local bundling.

    Commands are chained with ``&&``::

       {
          // Run tests prior to bundling
          beforeBundling(inputDir: string, outputDir: string): string[] {
            return [`go test -mod=vendor ./...`];
          }
          // ...
       }

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-lambda-go-alpha.ICommandHooks"

    @jsii.member(jsii_name="afterBundling")
    def after_bundling(
        self,
        input_dir: builtins.str,
        output_dir: builtins.str,
    ) -> typing.List[builtins.str]:
        '''(experimental) Returns commands to run after bundling.

        Commands are chained with ``&&``.

        :param input_dir: -
        :param output_dir: -

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "afterBundling", [input_dir, output_dir]))

    @jsii.member(jsii_name="beforeBundling")
    def before_bundling(
        self,
        input_dir: builtins.str,
        output_dir: builtins.str,
    ) -> typing.List[builtins.str]:
        '''(experimental) Returns commands to run before bundling.

        Commands are chained with ``&&``.

        :param input_dir: -
        :param output_dir: -

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "beforeBundling", [input_dir, output_dir]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICommandHooks).__jsii_proxy_class__ = lambda : _ICommandHooksProxy


__all__ = [
    "BundlingOptions",
    "GoFunction",
    "GoFunctionProps",
    "ICommandHooks",
]

publication.publish()
