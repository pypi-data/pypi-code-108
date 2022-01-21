'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-autoscaling-gitlab-runner?style=flat-square)](https://github.com/pepperize/cdk-autoscaling-gitlab-runner/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-autoscaling-gitlab-runner?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-autoscaling-gitlab-runner)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-autoscaling-gitlab-runner?style=flat-square)](https://pypi.org/project/pepperize.cdk-autoscaling-gitlab-runner/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.AutoscalingGitlabRunner?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.AutoscalingGitlabRunner/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-autoscaling-gitlab-runner/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-autoscaling-gitlab-runner/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-autoscaling-gitlab-runner?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-autoscaling-gitlab-runner/releases)

# AWS CDK GitLab Runner autoscaling on EC2

This project provides a CDK construct to [execute jobs on auto-scaled EC2 instances](https://docs.gitlab.com/runner/configuration/runner_autoscale_aws/index.html) using the [Docker Machine](https://docs.gitlab.com/runner/executors/docker_machine.html) executor.

> Running out of [Runner minutes](https://about.gitlab.com/pricing/),
> using [Docker-in-Docker (dind)](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html),
> speed up jobs with [shared S3 Cache](https://docs.gitlab.com/runner/configuration/autoscale.html#distributed-runners-caching),
> cross compiling/building environment [multiarch](https://hub.docker.com/r/multiarch/qemu-user-static/),
> cost effective [autoscaling on EC2](https://docs.gitlab.com/runner/configuration/runner_autoscale_aws/#the-runnersmachine-section),
> deploy directly from AWS accounts (without [AWS Access Key](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)),
> running on [Spot instances](https://aws.amazon.com/ec2/spot/),
> having a bigger [build log size](https://docs.gitlab.com/runner/configuration/advanced-configuration.html)

## Install

### TypeScript

```shell
npm install @pepperize/cdk-autoscaling-gitlab-runner
```

or

```shell
yarn add @pepperize/cdk-autoscaling-gitlab-runner
```

### Python

```shell
pip install pepperize.cdk-autoscaling-gitlab-runner
```

### C# / .Net

```
dotnet add package Pepperize.CDK.AutoscalingGitlabRunner
```

## Quickstart

1. **Create a new AWS CDK App** in TypeScript with [projen](https://github.com/projen/projen)

   ```shell
   mkdir gitlab-runner
   cd gitlab-runner
   git init
   npx projen new awscdk-app-ts
   ```
2. **Configure your project in `.projenrc.js`**

   * Add `deps: ["@pepperize/cdk-autoscaling-gitlab-runner"],`
3. **Update project files and install dependencies**

   ```shell
   npx projen
   ```
4. **Register a new runner**

   [Registering runners](https://docs.gitlab.com/runner/register/):

   * For a [shared runner](https://docs.gitlab.com/ee/ci/runners/#shared-runners), go to the GitLab Admin Area and click **Overview > Runners**
   * For a [group runner](https://docs.gitlab.com/ee/ci/runners/index.html#group-runners), go to **Settings > CI/CD** and expand the **Runners** section
   * For a [project runner](https://docs.gitlab.com/ee/ci/runners/index.html#specific-runners), go to **Settings > CI/CD** and expand the **Runners** section

   *Optionally enable: **Run untagged jobs** [x]
   Indicates whether this runner can pick jobs without tags*

   See also *[Registration token vs. Authentication token](https://docs.gitlab.com/ee/api/runners.html#registration-and-authentication-tokens)*
5. **Retrieve a new runner authentication token**

   [Register a new runner](https://docs.gitlab.com/ee/api/runners.html#register-a-new-runner)

   ```shell
   curl --request POST "https://gitlab.com/api/v4/runners" --form "token=<your register token>" --form "description=gitlab-runner" --form "tag_list=pepperize,docker,production"
   ```
6. **Add to your `main.ts`**

   ```python
   import { Vpc } from "@aws-cdk/aws-ec2";
   import { App, Stack } from "@aws-cdk/core";
   import { GitlabRunnerAutoscaling } from "@pepperize/cdk-autoscaling-gitlab-runner";

   const app = new App();
   const stack = new Stack(app, "GitLabRunnerStack");
   const vpc = Vpc.fromLookup(app, "ExistingVpc", {
     vpcId: "<your vpc id>",
   });
   new GitlabRunnerAutoscaling(stack, "GitlabRunner", {
     gitlabToken: "<your gitlab runner auth token>",
     network: {
       vpc,
     },
   });
   ```
7. **Create service linked role**

   *(If requesting spot instances, default: true)*

   ```sh
   aws iam create-service-linked-role --aws-service-name spot.amazonaws.com
   ```
8. **Configure the AWS CLI**

   * [AWSume](https://awsu.me/)
   * [Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
   * [AWS Single Sign-On](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html)
9. **Deploy the GitLab Runner**

   ```shell
   npm run deploy
   ```

## Example

### Custom cache bucket

By default an AWS S3 is created as GitLab Runner's distributed cache.
It's encrypted with a KMS managed key and public access is blocked.
A custom S3 Bucket can be configured.

```python
const cache = new Bucket(this, "Cache", {
  // Your custom bucket
});

new GitlabRunnerAutoscaling(this, "Runner", {
  gitlabToken: "<auth token>",
  cache: { bucket: cache },
});
```

See [example](https://github.com/pepperize/cdk-autoscaling-gitlab-runner-example/blob/main/src/cache.ts)

### Configure Docker Machine

By default, docker machine is configured to run privileged with `CAP_SYS_ADMIN` to support [Docker-in-Docker using the OverlayFS driver](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html#use-the-overlayfs-driver)
and cross compiling/building with [multiarch](https://hub.docker.com/r/multiarch/qemu-user-static/).

See [runners.docker section](https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section)
in [Advanced configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration.html)

```python
import { GitlabRunnerAutoscaling } from "@pepperize/cdk-autoscaling-gitlab-runner";

new GitlabRunnerAutoscaling(this, "Runner", {
  gitlabToken: "<auth token>",
  runners: {
    environment: [], // Reset the OverlayFS driver for every project
    docker: {
      capAdd: [], // Remove the CAP_SYS_ADMIN
      privileged: false, // Run unprivileged
    },
    machine: {
      idleCount: 2, // Number of idle machine
      idleTime: 3000, // Waiting time in idle state
      maxBuilds: 1, // Max builds before instance is removed
    },
  },
});
```

See [example](https://github.com/pepperize/cdk-autoscaling-gitlab-runner-example/blob/main/src/docker-machine.ts)

### Bigger instance type

By default, t3.nano is used for the manager/coordinator and t3.micro instances will be spawned.
For bigger projects, for example with [webpack](https://webpack.js.org/), this won't be enough memory.

```python
new GitlabRunnerAutoscaling(this, "Runner", {
  gitlabToken: "<auth token>",
  manager: {
    instanceType: InstanceType.of(InstanceClass.T3, InstanceSize.NANO),
  },
  runners: {
    instanceType: InstanceType.of(InstanceClass.T3, InstanceSize.LARGE),
  },
});
```

See [example](https://github.com/pepperize/cdk-autoscaling-gitlab-runner-example/blob/main/src/instance-type.ts)

### Different machine image

By default, the latest [Amazon 2 Linux](https://aws.amazon.com/amazon-linux-2/) will be used for the manager/coordinator.
The manager/coordinator instance's cloud init scripts requires [yum](https://access.redhat.com/solutions/9934) is installed, any RHEL flavor should work.
The requested runner instances by default using Ubuntu 20.04, any OS implemented by the [Docker Machine provisioner](https://gitlab.com/gitlab-org/ci-cd/docker-machine/-/tree/main/libmachine/provision) should work.

```python
new GitlabRunnerAutoscaling(this, "Runner", {
  gitlabToken: "<auth token>",
  manager: {
    machineImage: MachineImage.genericLinux(managerAmiMap),
  },
  runners: {
    machineImage: MachineImage.genericLinux(runnerAmiMap),
  },
});
```

See [example](https://github.com/pepperize/cdk-autoscaling-gitlab-runner-example/blob/main/src/machine-image.ts)

### Spot instances

By default, EC2 Spot Instances are requested.

```python
new GitlabRunnerAutoscaling(this, "Runner", {
  gitlabToken: "<auth token>",
  runners: {
    machine: {
      machineOptions: {
        requestSpotInstance: false,
        spotPrice: 0.5,
      },
    },
  },
});
```

See [example](https://github.com/pepperize/cdk-autoscaling-gitlab-runner-example/blob/main/src/on-demand-instances.ts)

### Custom runner's role

To deploy from within your GitLab Runner Instances, you may pass a Role with the IAM Policies attached.

```python
const role = new Role(this, "RunnersRole", {
  assumedBy: new ServicePrincipal("ec2.amazonaws.com", {}),
  inlinePolicies: {},
});

new GitlabRunnerAutoscaling(this, "Runner", {
  gitlabToken: "<auth token>",
  runners: {
    role: role,
  },
});
```

See [example](https://github.com/pepperize/cdk-autoscaling-gitlab-runner-example/blob/main/src/runner-role.ts)

### Vpc

If no existing Vpc is passed, a [VPC that spans a whole region](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.Vpc.html) on will be created.
This can become costly, because AWS CDK configured also the routing for the private subnets and creates NAT Gateways (one per AZ).

```python
const vpc = new Vpc(this, "Vpc", {
  // Your custom vpc
});

new GitlabRunnerAutoscaling(this, "Runner", {
  gitlabToken: "<auth token>",
  network: { vpc: vpc },
});
```

See [example](https://github.com/pepperize/cdk-autoscaling-gitlab-runner-example/blob/main/src/vpc.ts)

### Zero config

Deploys the [Autoscaling GitLab Runner on AWS EC2](https://docs.gitlab.com/runner/configuration/runner_autoscale_aws/) with the default settings mentioned above.

Happy with the presets?

```python
new GitlabRunnerAutoscaling(this, "Runner", {
  gitlabToken: "<auth token>",
});
```

See [example](https://github.com/pepperize/cdk-autoscaling-gitlab-runner-example/blob/main/src/zero-config.ts)

## Projen

This project uses [projen](https://github.com/projen/projen) to maintain project configuration through code. Thus, the synthesized files with projen should never be manually edited (in fact, projen enforces that).

To modify the project setup, you should interact with rich strongly-typed
class [AwsCdkTypeScriptApp](https://github.com/projen/projen/blob/master/API.md#projen-awscdktypescriptapp) and
execute `npx projen` to update project configuration files.

> In simple words, developers can only modify `.projenrc.js` file for configuration/maintenance and files under `/src` directory for development.

See also [Create and Publish CDK Constructs Using projen and jsii](https://github.com/seeebiii/projen-test).
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

import aws_cdk.aws_autoscaling
import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_s3
import aws_cdk.core


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.AutoscalingConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "idle_count": "idleCount",
        "idle_time": "idleTime",
        "periods": "periods",
        "timezone": "timezone",
    },
)
class AutoscalingConfiguration:
    def __init__(
        self,
        *,
        idle_count: typing.Optional[jsii.Number] = None,
        idle_time: typing.Optional[jsii.Number] = None,
        periods: typing.Optional[typing.Sequence[builtins.str]] = None,
        timezone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param idle_count: 
        :param idle_time: 
        :param periods: The Periods setting contains an array of string patterns of time periods represented in a cron-style format. https://github.com/gorhill/cronexpr#implementation. [second] [minute] [hour] [day of month] [month] [day of week] [year]
        :param timezone: 

        :see: https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersmachineautoscaling-sections
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if idle_count is not None:
            self._values["idle_count"] = idle_count
        if idle_time is not None:
            self._values["idle_time"] = idle_time
        if periods is not None:
            self._values["periods"] = periods
        if timezone is not None:
            self._values["timezone"] = timezone

    @builtins.property
    def idle_count(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("idle_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def idle_time(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("idle_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def periods(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The Periods setting contains an array of string patterns of time periods represented in a cron-style format. https://github.com/gorhill/cronexpr#implementation.

        [second] [minute] [hour] [day of month] [month] [day of week] [year]

        Example::

            // "* * 7-22 * * mon-fri *"
        '''
        result = self._values.get("periods")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Cache(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.Cache",
):
    '''A GitLab Runner cache consisting of an Amazon S3 bucket.

    The bucket is encrypted with a KMS managed master key, it has public access blocked and will be cleared and deleted on CFN stack deletion.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Stack,
        id: builtins.str,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        expiration: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: The infix of the physical cache bucket name. Default: "runner-cache"
        :param expiration: The number of days after which the created cache objects are deleted from S3. Default: 30 days
        '''
        props = CacheProps(bucket_name=bucket_name, expiration=expiration)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.IBucket:
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucket"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.CacheConfiguration",
    jsii_struct_bases=[],
    name_mapping={"s3": "s3", "shared": "shared", "type": "type"},
)
class CacheConfiguration:
    def __init__(
        self,
        *,
        s3: typing.Optional["CacheS3Configuration"] = None,
        shared: typing.Optional[builtins.bool] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param s3: 
        :param shared: 
        :param type: 
        '''
        if isinstance(s3, dict):
            s3 = CacheS3Configuration(**s3)
        self._values: typing.Dict[str, typing.Any] = {}
        if s3 is not None:
            self._values["s3"] = s3
        if shared is not None:
            self._values["shared"] = shared
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def s3(self) -> typing.Optional["CacheS3Configuration"]:
        result = self._values.get("s3")
        return typing.cast(typing.Optional["CacheS3Configuration"], result)

    @builtins.property
    def shared(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("shared")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CacheConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.CacheProps",
    jsii_struct_bases=[],
    name_mapping={"bucket_name": "bucketName", "expiration": "expiration"},
)
class CacheProps:
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        expiration: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param bucket_name: The infix of the physical cache bucket name. Default: "runner-cache"
        :param expiration: The number of days after which the created cache objects are deleted from S3. Default: 30 days
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if expiration is not None:
            self._values["expiration"] = expiration

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''The infix of the physical cache bucket name.

        :default: "runner-cache"
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expiration(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The number of days after which the created cache objects are deleted from S3.

        :default: 30 days
        '''
        result = self._values.get("expiration")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CacheProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.CacheS3Configuration",
    jsii_struct_bases=[],
    name_mapping={
        "access_key": "accessKey",
        "bucket_location": "bucketLocation",
        "bucket_name": "bucketName",
        "secret_key": "secretKey",
        "server_address": "serverAddress",
    },
)
class CacheS3Configuration:
    def __init__(
        self,
        *,
        access_key: typing.Optional[builtins.str] = None,
        bucket_location: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        secret_key: typing.Optional[builtins.str] = None,
        server_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_key: 
        :param bucket_location: The name of the S3 region.
        :param bucket_name: The name of the storage bucket where cache is stored. Default: "runners-cache"
        :param secret_key: 
        :param server_address: The AWS S3 host. Default: "s3.amazonaws.com"
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if access_key is not None:
            self._values["access_key"] = access_key
        if bucket_location is not None:
            self._values["bucket_location"] = bucket_location
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if secret_key is not None:
            self._values["secret_key"] = secret_key
        if server_address is not None:
            self._values["server_address"] = server_address

    @builtins.property
    def access_key(self) -> typing.Optional[builtins.str]:
        result = self._values.get("access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_location(self) -> typing.Optional[builtins.str]:
        '''The name of the S3 region.'''
        result = self._values.get("bucket_location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''The name of the storage bucket where cache is stored.

        :default: "runners-cache"
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[builtins.str]:
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_address(self) -> typing.Optional[builtins.str]:
        '''The AWS S3 host.

        :default: "s3.amazonaws.com"
        '''
        result = self._values.get("server_address")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CacheS3Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigurationMapper(
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.ConfigurationMapper",
):
    @jsii.member(jsii_name="fromProps") # type: ignore[misc]
    @builtins.classmethod
    def from_props(
        cls,
        *,
        autoscaling_configurations: typing.Sequence[AutoscalingConfiguration],
        cache_configuration: CacheConfiguration,
        docker_configuration: "DockerConfiguration",
        global_configuration: "GlobalConfiguration",
        machine_configuration: "MachineConfiguration",
        runner_configuration: "RunnerConfiguration",
    ) -> "ConfigurationMapper":
        '''
        :param autoscaling_configurations: 
        :param cache_configuration: 
        :param docker_configuration: 
        :param global_configuration: 
        :param machine_configuration: 
        :param runner_configuration: 
        '''
        props = ConfigurationMapperProps(
            autoscaling_configurations=autoscaling_configurations,
            cache_configuration=cache_configuration,
            docker_configuration=docker_configuration,
            global_configuration=global_configuration,
            machine_configuration=machine_configuration,
            runner_configuration=runner_configuration,
        )

        return typing.cast("ConfigurationMapper", jsii.sinvoke(cls, "fromProps", [props]))

    @jsii.member(jsii_name="withDefaults") # type: ignore[misc]
    @builtins.classmethod
    def with_defaults(
        cls,
        *,
        autoscaling_configurations: typing.Sequence[AutoscalingConfiguration],
        cache_configuration: CacheConfiguration,
        docker_configuration: "DockerConfiguration",
        global_configuration: "GlobalConfiguration",
        machine_configuration: "MachineConfiguration",
        runner_configuration: "RunnerConfiguration",
    ) -> "ConfigurationMapper":
        '''
        :param autoscaling_configurations: 
        :param cache_configuration: 
        :param docker_configuration: 
        :param global_configuration: 
        :param machine_configuration: 
        :param runner_configuration: 
        '''
        props = ConfigurationMapperProps(
            autoscaling_configurations=autoscaling_configurations,
            cache_configuration=cache_configuration,
            docker_configuration=docker_configuration,
            global_configuration=global_configuration,
            machine_configuration=machine_configuration,
            runner_configuration=runner_configuration,
        )

        return typing.cast("ConfigurationMapper", jsii.sinvoke(cls, "withDefaults", [props]))

    @jsii.member(jsii_name="toToml")
    def to_toml(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toToml", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> "ConfigurationMapperProps":
        return typing.cast("ConfigurationMapperProps", jsii.get(self, "props"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.ConfigurationMapperProps",
    jsii_struct_bases=[],
    name_mapping={
        "autoscaling_configurations": "autoscalingConfigurations",
        "cache_configuration": "cacheConfiguration",
        "docker_configuration": "dockerConfiguration",
        "global_configuration": "globalConfiguration",
        "machine_configuration": "machineConfiguration",
        "runner_configuration": "runnerConfiguration",
    },
)
class ConfigurationMapperProps:
    def __init__(
        self,
        *,
        autoscaling_configurations: typing.Sequence[AutoscalingConfiguration],
        cache_configuration: CacheConfiguration,
        docker_configuration: "DockerConfiguration",
        global_configuration: "GlobalConfiguration",
        machine_configuration: "MachineConfiguration",
        runner_configuration: "RunnerConfiguration",
    ) -> None:
        '''
        :param autoscaling_configurations: 
        :param cache_configuration: 
        :param docker_configuration: 
        :param global_configuration: 
        :param machine_configuration: 
        :param runner_configuration: 
        '''
        if isinstance(cache_configuration, dict):
            cache_configuration = CacheConfiguration(**cache_configuration)
        if isinstance(docker_configuration, dict):
            docker_configuration = DockerConfiguration(**docker_configuration)
        if isinstance(global_configuration, dict):
            global_configuration = GlobalConfiguration(**global_configuration)
        if isinstance(machine_configuration, dict):
            machine_configuration = MachineConfiguration(**machine_configuration)
        if isinstance(runner_configuration, dict):
            runner_configuration = RunnerConfiguration(**runner_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "autoscaling_configurations": autoscaling_configurations,
            "cache_configuration": cache_configuration,
            "docker_configuration": docker_configuration,
            "global_configuration": global_configuration,
            "machine_configuration": machine_configuration,
            "runner_configuration": runner_configuration,
        }

    @builtins.property
    def autoscaling_configurations(self) -> typing.List[AutoscalingConfiguration]:
        result = self._values.get("autoscaling_configurations")
        assert result is not None, "Required property 'autoscaling_configurations' is missing"
        return typing.cast(typing.List[AutoscalingConfiguration], result)

    @builtins.property
    def cache_configuration(self) -> CacheConfiguration:
        result = self._values.get("cache_configuration")
        assert result is not None, "Required property 'cache_configuration' is missing"
        return typing.cast(CacheConfiguration, result)

    @builtins.property
    def docker_configuration(self) -> "DockerConfiguration":
        result = self._values.get("docker_configuration")
        assert result is not None, "Required property 'docker_configuration' is missing"
        return typing.cast("DockerConfiguration", result)

    @builtins.property
    def global_configuration(self) -> "GlobalConfiguration":
        result = self._values.get("global_configuration")
        assert result is not None, "Required property 'global_configuration' is missing"
        return typing.cast("GlobalConfiguration", result)

    @builtins.property
    def machine_configuration(self) -> "MachineConfiguration":
        result = self._values.get("machine_configuration")
        assert result is not None, "Required property 'machine_configuration' is missing"
        return typing.cast("MachineConfiguration", result)

    @builtins.property
    def runner_configuration(self) -> "RunnerConfiguration":
        result = self._values.get("runner_configuration")
        assert result is not None, "Required property 'runner_configuration' is missing"
        return typing.cast("RunnerConfiguration", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigurationMapperProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.DockerConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_images": "allowedImages",
        "allowed_services": "allowedServices",
        "cache_dir": "cacheDir",
        "cap_add": "capAdd",
        "cap_drop": "capDrop",
        "cpus": "cpus",
        "cpuset_cpus": "cpusetCpus",
        "cpu_shares": "cpuShares",
        "devices": "devices",
        "disable_cache": "disableCache",
        "disable_entrypoint_overwrite": "disableEntrypointOverwrite",
        "dns": "dns",
        "dns_search": "dnsSearch",
        "extra_hosts": "extraHosts",
        "gpus": "gpus",
        "helper_image": "helperImage",
        "helper_image_flavor": "helperImageFlavor",
        "host": "host",
        "hostname": "hostname",
        "image": "image",
        "links": "links",
        "memory": "memory",
        "memory_reservation": "memoryReservation",
        "memory_swap": "memorySwap",
        "network_mode": "networkMode",
        "oom_kill_disable": "oomKillDisable",
        "oom_score_adjust": "oomScoreAdjust",
        "privileged": "privileged",
        "pull_policy": "pullPolicy",
        "runtime": "runtime",
        "security_opt": "securityOpt",
        "shm_size": "shmSize",
        "sysctls": "sysctls",
        "tls_cert_path": "tlsCertPath",
        "tls_verify": "tlsVerify",
        "userns_mode": "usernsMode",
        "volume_driver": "volumeDriver",
        "volumes": "volumes",
        "volumes_from": "volumesFrom",
        "wait_for_services_timeout": "waitForServicesTimeout",
    },
)
class DockerConfiguration:
    def __init__(
        self,
        *,
        allowed_images: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_services: typing.Optional[typing.Sequence[builtins.str]] = None,
        cache_dir: typing.Optional[builtins.str] = None,
        cap_add: typing.Optional[typing.Sequence[builtins.str]] = None,
        cap_drop: typing.Optional[typing.Sequence[builtins.str]] = None,
        cpus: typing.Optional[builtins.str] = None,
        cpuset_cpus: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        devices: typing.Optional[typing.Sequence[builtins.str]] = None,
        disable_cache: typing.Optional[builtins.bool] = None,
        disable_entrypoint_overwrite: typing.Optional[builtins.bool] = None,
        dns: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_search: typing.Optional[typing.Sequence[builtins.str]] = None,
        extra_hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
        gpus: typing.Optional[typing.Sequence[builtins.str]] = None,
        helper_image: typing.Optional[builtins.str] = None,
        helper_image_flavor: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        hostname: typing.Optional[builtins.str] = None,
        image: typing.Optional[builtins.str] = None,
        links: typing.Optional[typing.Sequence[builtins.str]] = None,
        memory: typing.Optional[builtins.str] = None,
        memory_reservation: typing.Optional[builtins.str] = None,
        memory_swap: typing.Optional[builtins.str] = None,
        network_mode: typing.Optional[builtins.str] = None,
        oom_kill_disable: typing.Optional[builtins.bool] = None,
        oom_score_adjust: typing.Optional[builtins.str] = None,
        privileged: typing.Optional[builtins.bool] = None,
        pull_policy: typing.Optional[builtins.str] = None,
        runtime: typing.Optional[builtins.str] = None,
        security_opt: typing.Optional[builtins.str] = None,
        shm_size: typing.Optional[jsii.Number] = None,
        sysctls: typing.Optional[builtins.str] = None,
        tls_cert_path: typing.Optional[builtins.str] = None,
        tls_verify: typing.Optional[builtins.bool] = None,
        userns_mode: typing.Optional[builtins.str] = None,
        volume_driver: typing.Optional[builtins.str] = None,
        volumes: typing.Optional[typing.Sequence[builtins.str]] = None,
        volumes_from: typing.Optional[typing.Sequence[builtins.str]] = None,
        wait_for_services_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Configure docker on the runners.

        :param allowed_images: Wildcard list of images that can be specified in the .gitlab-ci.yml file. If not present, all images are allowed (equivalent to ["*/*:*"]). See Restrict Docker images and services.
        :param allowed_services: Wildcard list of services that can be specified in the .gitlab-ci.yml file. If not present, all images are allowed (equivalent to [*/*:*]). See Restrict Docker images and services.
        :param cache_dir: Directory where Docker caches should be stored. This path can be absolute or relative to current working directory. See disable_cache for more information.
        :param cap_add: Add additional Linux capabilities to the container. Default: ["CAP_SYS_ADMIN"]
        :param cap_drop: Drop additional Linux capabilities from the container.
        :param cpus: Number of CPUs (available in Docker 1.13 or later. A string.
        :param cpuset_cpus: The control group’s CpusetCpus. A string.
        :param cpu_shares: Number of CPU shares used to set relative CPU usage. Default is 1024.
        :param devices: Share additional host devices with the container.
        :param disable_cache: The Docker executor has two levels of caching: a global one (like any other executor) and a local cache based on Docker volumes. This configuration flag acts only on the local one which disables the use of automatically created (not mapped to a host directory) cache volumes. In other words, it only prevents creating a container that holds temporary files of builds, it does not disable the cache if the runner is configured in distributed cache mode. Default: false
        :param disable_entrypoint_overwrite: Disable the image entrypoint overwriting.
        :param dns: A list of DNS servers for the container to use.
        :param dns_search: A list of DNS search domains.
        :param extra_hosts: Hosts that should be defined in container environment.
        :param gpus: GPU devices for Docker container. Uses the same format as the docker cli. View details in the Docker documentation.
        :param helper_image: (Advanced) The default helper image used to clone repositories and upload artifacts.
        :param helper_image_flavor: Sets the helper image flavor (alpine, alpine3.12, alpine3.13, alpine3.14 or ubuntu). Defaults to alpine. The alpine flavor uses the same version as alpine3.12.
        :param host: Custom Docker endpoint. Default is DOCKER_HOST environment or unix:///var/run/docker.sock.
        :param hostname: Custom hostname for the Docker container.
        :param image: The image to run jobs with.
        :param links: Containers that should be linked with container that runs the job.
        :param memory: The memory limit. A string.
        :param memory_reservation: The memory soft limit. A string.
        :param memory_swap: The total memory limit. A string.
        :param network_mode: Add container to a custom network.
        :param oom_kill_disable: If an out-of-memory (OOM) error occurs, do not kill processes in a container.
        :param oom_score_adjust: OOM score adjustment. Positive means kill earlier.
        :param privileged: Make the container run in privileged mode. Insecure. Default: true
        :param pull_policy: The image pull policy: never, if-not-present or always (default). View details in the pull policies documentation. You can also add multiple pull policies.
        :param runtime: The runtime for the Docker container.
        :param security_opt: Security options (–security-opt in docker run). Takes a list of : separated key/values.
        :param shm_size: Shared memory size for images (in bytes). Default: 0
        :param sysctls: The sysctl options.
        :param tls_cert_path: A directory where ca.pem, cert.pem or key.pem are stored and used to make a secure TLS connection to Docker. Useful in boot2docker.
        :param tls_verify: Enable or disable TLS verification of connections to Docker daemon. Disabled by default. Default: false
        :param userns_mode: The user namespace mode for the container and Docker services when user namespace remapping option is enabled. Available in Docker 1.10 or later.
        :param volume_driver: The volume driver to use for the container.
        :param volumes: Additional volumes that should be mounted. Same syntax as the Docker -v flag.
        :param volumes_from: A list of volumes to inherit from another container in the form [:<ro|rw>]. Access level defaults to read-write, but can be manually set to ro (read-only) or rw (read-write).
        :param wait_for_services_timeout: How long to wait for Docker services. Set to 0 to disable. Default is 30. Default: 300

        :see: https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if allowed_images is not None:
            self._values["allowed_images"] = allowed_images
        if allowed_services is not None:
            self._values["allowed_services"] = allowed_services
        if cache_dir is not None:
            self._values["cache_dir"] = cache_dir
        if cap_add is not None:
            self._values["cap_add"] = cap_add
        if cap_drop is not None:
            self._values["cap_drop"] = cap_drop
        if cpus is not None:
            self._values["cpus"] = cpus
        if cpuset_cpus is not None:
            self._values["cpuset_cpus"] = cpuset_cpus
        if cpu_shares is not None:
            self._values["cpu_shares"] = cpu_shares
        if devices is not None:
            self._values["devices"] = devices
        if disable_cache is not None:
            self._values["disable_cache"] = disable_cache
        if disable_entrypoint_overwrite is not None:
            self._values["disable_entrypoint_overwrite"] = disable_entrypoint_overwrite
        if dns is not None:
            self._values["dns"] = dns
        if dns_search is not None:
            self._values["dns_search"] = dns_search
        if extra_hosts is not None:
            self._values["extra_hosts"] = extra_hosts
        if gpus is not None:
            self._values["gpus"] = gpus
        if helper_image is not None:
            self._values["helper_image"] = helper_image
        if helper_image_flavor is not None:
            self._values["helper_image_flavor"] = helper_image_flavor
        if host is not None:
            self._values["host"] = host
        if hostname is not None:
            self._values["hostname"] = hostname
        if image is not None:
            self._values["image"] = image
        if links is not None:
            self._values["links"] = links
        if memory is not None:
            self._values["memory"] = memory
        if memory_reservation is not None:
            self._values["memory_reservation"] = memory_reservation
        if memory_swap is not None:
            self._values["memory_swap"] = memory_swap
        if network_mode is not None:
            self._values["network_mode"] = network_mode
        if oom_kill_disable is not None:
            self._values["oom_kill_disable"] = oom_kill_disable
        if oom_score_adjust is not None:
            self._values["oom_score_adjust"] = oom_score_adjust
        if privileged is not None:
            self._values["privileged"] = privileged
        if pull_policy is not None:
            self._values["pull_policy"] = pull_policy
        if runtime is not None:
            self._values["runtime"] = runtime
        if security_opt is not None:
            self._values["security_opt"] = security_opt
        if shm_size is not None:
            self._values["shm_size"] = shm_size
        if sysctls is not None:
            self._values["sysctls"] = sysctls
        if tls_cert_path is not None:
            self._values["tls_cert_path"] = tls_cert_path
        if tls_verify is not None:
            self._values["tls_verify"] = tls_verify
        if userns_mode is not None:
            self._values["userns_mode"] = userns_mode
        if volume_driver is not None:
            self._values["volume_driver"] = volume_driver
        if volumes is not None:
            self._values["volumes"] = volumes
        if volumes_from is not None:
            self._values["volumes_from"] = volumes_from
        if wait_for_services_timeout is not None:
            self._values["wait_for_services_timeout"] = wait_for_services_timeout

    @builtins.property
    def allowed_images(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Wildcard list of images that can be specified in the .gitlab-ci.yml file. If not present, all images are allowed (equivalent to ["*/*:*"]). See Restrict Docker images and services.'''
        result = self._values.get("allowed_images")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_services(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Wildcard list of services that can be specified in the .gitlab-ci.yml file. If not present, all images are allowed (equivalent to [*/*:*]). See Restrict Docker images and services.'''
        result = self._values.get("allowed_services")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cache_dir(self) -> typing.Optional[builtins.str]:
        '''Directory where Docker caches should be stored.

        This path can be absolute or relative to current working directory. See disable_cache for more information.
        '''
        result = self._values.get("cache_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cap_add(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Add additional Linux capabilities to the container.

        :default: ["CAP_SYS_ADMIN"]
        '''
        result = self._values.get("cap_add")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cap_drop(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Drop additional Linux capabilities from the container.'''
        result = self._values.get("cap_drop")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cpus(self) -> typing.Optional[builtins.str]:
        '''Number of CPUs (available in Docker 1.13 or later. A string.'''
        result = self._values.get("cpus")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpuset_cpus(self) -> typing.Optional[builtins.str]:
        '''The control group’s CpusetCpus.

        A string.
        '''
        result = self._values.get("cpuset_cpus")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_shares(self) -> typing.Optional[jsii.Number]:
        '''Number of CPU shares used to set relative CPU usage.

        Default is 1024.
        '''
        result = self._values.get("cpu_shares")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def devices(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Share additional host devices with the container.'''
        result = self._values.get("devices")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disable_cache(self) -> typing.Optional[builtins.bool]:
        '''The Docker executor has two levels of caching: a global one (like any other executor) and a local cache based on Docker volumes.

        This configuration flag acts only on the local one which disables the use of automatically created (not mapped to a host directory) cache volumes. In other words, it only prevents creating a container that holds temporary files of builds, it does not disable the cache if the runner is configured in distributed cache mode.

        :default: false
        '''
        result = self._values.get("disable_cache")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_entrypoint_overwrite(self) -> typing.Optional[builtins.bool]:
        '''Disable the image entrypoint overwriting.'''
        result = self._values.get("disable_entrypoint_overwrite")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of DNS servers for the container to use.'''
        result = self._values.get("dns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dns_search(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of DNS search domains.'''
        result = self._values.get("dns_search")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def extra_hosts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Hosts that should be defined in container environment.'''
        result = self._values.get("extra_hosts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def gpus(self) -> typing.Optional[typing.List[builtins.str]]:
        '''GPU devices for Docker container.

        Uses the same format as the docker cli. View details in the Docker documentation.
        '''
        result = self._values.get("gpus")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def helper_image(self) -> typing.Optional[builtins.str]:
        '''(Advanced) The default helper image used to clone repositories and upload artifacts.'''
        result = self._values.get("helper_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def helper_image_flavor(self) -> typing.Optional[builtins.str]:
        '''Sets the helper image flavor (alpine, alpine3.12, alpine3.13, alpine3.14 or ubuntu). Defaults to alpine. The alpine flavor uses the same version as alpine3.12.'''
        result = self._values.get("helper_image_flavor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Custom Docker endpoint.

        Default is DOCKER_HOST environment or unix:///var/run/docker.sock.
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''Custom hostname for the Docker container.'''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        '''The image to run jobs with.'''
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def links(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Containers that should be linked with container that runs the job.'''
        result = self._values.get("links")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def memory(self) -> typing.Optional[builtins.str]:
        '''The memory limit.

        A string.
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory_reservation(self) -> typing.Optional[builtins.str]:
        '''The memory soft limit.

        A string.
        '''
        result = self._values.get("memory_reservation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory_swap(self) -> typing.Optional[builtins.str]:
        '''The total memory limit.

        A string.
        '''
        result = self._values.get("memory_swap")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_mode(self) -> typing.Optional[builtins.str]:
        '''Add container to a custom network.'''
        result = self._values.get("network_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oom_kill_disable(self) -> typing.Optional[builtins.bool]:
        '''If an out-of-memory (OOM) error occurs, do not kill processes in a container.'''
        result = self._values.get("oom_kill_disable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def oom_score_adjust(self) -> typing.Optional[builtins.str]:
        '''OOM score adjustment.

        Positive means kill earlier.
        '''
        result = self._values.get("oom_score_adjust")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def privileged(self) -> typing.Optional[builtins.bool]:
        '''Make the container run in privileged mode.

        Insecure.

        :default: true
        '''
        result = self._values.get("privileged")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_policy(self) -> typing.Optional[builtins.str]:
        '''The image pull policy: never, if-not-present or always (default).

        View details in the pull policies documentation. You can also add multiple pull policies.
        '''
        result = self._values.get("pull_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runtime(self) -> typing.Optional[builtins.str]:
        '''The runtime for the Docker container.'''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_opt(self) -> typing.Optional[builtins.str]:
        '''Security options (–security-opt in docker run).

        Takes a list of : separated key/values.
        '''
        result = self._values.get("security_opt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def shm_size(self) -> typing.Optional[jsii.Number]:
        '''Shared memory size for images (in bytes).

        :default: 0
        '''
        result = self._values.get("shm_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sysctls(self) -> typing.Optional[builtins.str]:
        '''The sysctl options.'''
        result = self._values.get("sysctls")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_cert_path(self) -> typing.Optional[builtins.str]:
        '''A directory where ca.pem, cert.pem or key.pem are stored and used to make a secure TLS connection to Docker. Useful in boot2docker.'''
        result = self._values.get("tls_cert_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_verify(self) -> typing.Optional[builtins.bool]:
        '''Enable or disable TLS verification of connections to Docker daemon.

        Disabled by default.

        :default: false
        '''
        result = self._values.get("tls_verify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def userns_mode(self) -> typing.Optional[builtins.str]:
        '''The user namespace mode for the container and Docker services when user namespace remapping option is enabled.

        Available in Docker 1.10 or later.
        '''
        result = self._values.get("userns_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def volume_driver(self) -> typing.Optional[builtins.str]:
        '''The volume driver to use for the container.'''
        result = self._values.get("volume_driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional volumes that should be mounted.

        Same syntax as the Docker -v flag.
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def volumes_from(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of volumes to inherit from another container in the form [:<ro|rw>].

        Access level defaults to read-write, but can be manually set to ro (read-only) or rw (read-write).
        '''
        result = self._values.get("volumes_from")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def wait_for_services_timeout(self) -> typing.Optional[jsii.Number]:
        '''How long to wait for Docker services.

        Set to 0 to disable. Default is 30.

        :default: 300
        '''
        result = self._values.get("wait_for_services_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GitlabRunnerAutoscaling(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.GitlabRunnerAutoscaling",
):
    '''The Gitlab Runner autoscaling on EC2 by Docker Machine.

    Example::

        <caption>Provisioning a basic Runner</caption>
        const app = new cdk.App();
        const stack = new cdk.Stack(app, "RunnerStack", {
        env: {
        account: "000000000000",
        region: "us-east-1",
        }
        });
        
        new GitlabRunnerAutoscaling(scope, "GitlabRunner", {
        gitlabToken: "xxxxxxxxxxxxxxxxxxxx",
        });
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Stack,
        id: builtins.str,
        *,
        gitlab_token: builtins.str,
        cache: typing.Optional["GitlabRunnerAutoscalingCacheProps"] = None,
        gitlab_url: typing.Optional[builtins.str] = None,
        manager: typing.Optional["GitlabRunnerAutoscalingManagerProps"] = None,
        network: typing.Optional["NetworkProps"] = None,
        runners: typing.Optional["GitlabRunnerAutoscalingRunnerProps"] = None,
        check_interval: typing.Optional[jsii.Number] = None,
        concurrent: typing.Optional[jsii.Number] = None,
        log_format: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param gitlab_token: The GitLab Runner’s authentication token, which is obtained during runner registration.
        :param cache: 
        :param gitlab_url: GitLab instance URL. Default: "https://gitlab.com"
        :param manager: The manager EC2 instance configuration. If not set, the defaults will be used.
        :param network: The network configuration for the Runner. If not set, the defaults will be used.
        :param runners: 
        :param check_interval: The check_interval option defines how often the runner should check GitLab for new jobs| in seconds. Default: 0
        :param concurrent: The limit of the jobs that can be run concurrently across all runners (concurrent). Default: 10
        :param log_format: The log format. Default: "runner"
        :param log_level: The log_level. Default: "info"
        '''
        props = GitlabRunnerAutoscalingProps(
            gitlab_token=gitlab_token,
            cache=cache,
            gitlab_url=gitlab_url,
            manager=manager,
            network=network,
            runners=runners,
            check_interval=check_interval,
            concurrent=concurrent,
            log_format=log_format,
            log_level=log_level,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheBucket")
    def cache_bucket(self) -> aws_cdk.aws_s3.IBucket:
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "cacheBucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manager")
    def manager(self) -> "GitlabRunnerAutoscalingManager":
        return typing.cast("GitlabRunnerAutoscalingManager", jsii.get(self, "manager"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="network")
    def network(self) -> "Network":
        return typing.cast("Network", jsii.get(self, "network"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runners")
    def runners(self) -> "GitlabRunnerAutoscalingRunners":
        return typing.cast("GitlabRunnerAutoscalingRunners", jsii.get(self, "runners"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.GitlabRunnerAutoscalingCacheProps",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "options": "options"},
)
class GitlabRunnerAutoscalingCacheProps:
    def __init__(
        self,
        *,
        bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        options: typing.Optional[CacheProps] = None,
    ) -> None:
        '''The distributed GitLab runner S3 cache.

        Either pass an existing bucket or override default options.

        :param bucket: An existing S3 bucket used as runner's cache.
        :param options: If no existing S3 bucket is provided, a S3 bucket will be created.

        :see: https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnerscaches3-section
        '''
        if isinstance(options, dict):
            options = CacheProps(**options)
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket is not None:
            self._values["bucket"] = bucket
        if options is not None:
            self._values["options"] = options

    @builtins.property
    def bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''An existing S3 bucket used as runner's cache.'''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def options(self) -> typing.Optional[CacheProps]:
        '''If no existing S3 bucket is provided, a S3 bucket will be created.'''
        result = self._values.get("options")
        return typing.cast(typing.Optional[CacheProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabRunnerAutoscalingCacheProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.GitlabRunnerAutoscalingManager",
    jsii_struct_bases=[],
    name_mapping={
        "auto_scaling_group": "autoScalingGroup",
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "role": "role",
        "security_group": "securityGroup",
    },
)
class GitlabRunnerAutoscalingManager:
    def __init__(
        self,
        *,
        auto_scaling_group: aws_cdk.aws_autoscaling.IAutoScalingGroup,
        instance_type: aws_cdk.aws_ec2.InstanceType,
        machine_image: aws_cdk.aws_ec2.IMachineImage,
        role: aws_cdk.aws_iam.IRole,
        security_group: aws_cdk.aws_ec2.ISecurityGroup,
    ) -> None:
        '''
        :param auto_scaling_group: 
        :param instance_type: 
        :param machine_image: 
        :param role: 
        :param security_group: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "auto_scaling_group": auto_scaling_group,
            "instance_type": instance_type,
            "machine_image": machine_image,
            "role": role,
            "security_group": security_group,
        }

    @builtins.property
    def auto_scaling_group(self) -> aws_cdk.aws_autoscaling.IAutoScalingGroup:
        result = self._values.get("auto_scaling_group")
        assert result is not None, "Required property 'auto_scaling_group' is missing"
        return typing.cast(aws_cdk.aws_autoscaling.IAutoScalingGroup, result)

    @builtins.property
    def instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(aws_cdk.aws_ec2.InstanceType, result)

    @builtins.property
    def machine_image(self) -> aws_cdk.aws_ec2.IMachineImage:
        result = self._values.get("machine_image")
        assert result is not None, "Required property 'machine_image' is missing"
        return typing.cast(aws_cdk.aws_ec2.IMachineImage, result)

    @builtins.property
    def role(self) -> aws_cdk.aws_iam.IRole:
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(aws_cdk.aws_iam.IRole, result)

    @builtins.property
    def security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        result = self._values.get("security_group")
        assert result is not None, "Required property 'security_group' is missing"
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabRunnerAutoscalingManager(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.GitlabRunnerAutoscalingManagerProps",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "key_pair_name": "keyPairName",
        "machine_image": "machineImage",
    },
)
class GitlabRunnerAutoscalingManagerProps:
    def __init__(
        self,
        *,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        key_pair_name: typing.Optional[builtins.str] = None,
        machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
    ) -> None:
        '''
        :param instance_type: Instance type for manager EC2 instance. It's a combination of a class and size. Default: InstanceType.of(InstanceClass.T3, InstanceSize.NANO)
        :param key_pair_name: A set of security credentials that you use to prove your identity when connecting to an Amazon EC2 instance. You won't be able to ssh into an instance without the Key Pair.
        :param machine_image: An Amazon Machine Image ID for the Manager EC2 instance. If empty the latest Amazon 2 Image will be looked up. Should be RHEL flavor like Amazon Linux 2 with yum available for instance initialization.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if key_pair_name is not None:
            self._values["key_pair_name"] = key_pair_name
        if machine_image is not None:
            self._values["machine_image"] = machine_image

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''Instance type for manager EC2 instance.

        It's a combination of a class and size.

        :default: InstanceType.of(InstanceClass.T3, InstanceSize.NANO)
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def key_pair_name(self) -> typing.Optional[builtins.str]:
        '''A set of security credentials that you use to prove your identity when connecting to an Amazon EC2 instance.

        You won't be able to ssh into an instance without the Key Pair.
        '''
        result = self._values.get("key_pair_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def machine_image(self) -> typing.Optional[aws_cdk.aws_ec2.IMachineImage]:
        '''An Amazon Machine Image ID for the Manager EC2 instance.

        If empty the latest Amazon 2 Image will be looked up.

        Should be RHEL flavor like Amazon Linux 2 with yum available for instance initialization.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-init.html
        '''
        result = self._values.get("machine_image")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IMachineImage], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabRunnerAutoscalingManagerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.GitlabRunnerAutoscalingRunnerProps",
    jsii_struct_bases=[],
    name_mapping={
        "autoscaling": "autoscaling",
        "docker": "docker",
        "environment": "environment",
        "instance_type": "instanceType",
        "limit": "limit",
        "machine": "machine",
        "machine_image": "machineImage",
        "output_limit": "outputLimit",
        "role": "role",
    },
)
class GitlabRunnerAutoscalingRunnerProps:
    def __init__(
        self,
        *,
        autoscaling: typing.Optional[typing.Sequence[AutoscalingConfiguration]] = None,
        docker: typing.Optional[DockerConfiguration] = None,
        environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        limit: typing.Optional[jsii.Number] = None,
        machine: typing.Optional["MachineConfiguration"] = None,
        machine_image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        output_limit: typing.Optional[jsii.Number] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''The runner EC2 instances configuration.

        If not set, the defaults will be used.

        :param autoscaling: Optional autoscaling configuration.
        :param docker: Optional docker configuration.
        :param environment: Append or overwrite environment variables. Default: ["DOCKER_DRIVER=overlay2", "DOCKER_TLS_CERTDIR=/certs"]
        :param instance_type: Instance type for runner EC2 instances. It's a combination of a class and size. Default: InstanceType.of(InstanceClass.T3, InstanceSize.MICRO)
        :param limit: Limit how many jobs can be handled concurrently by this registered runner. 0 (default) means do not limit. Default: 10
        :param machine: Optional docker machine configuration.
        :param machine_image: An Amazon Machine Image ID for the Runners EC2 instances. If empty the latest Ubuntu 20.04 focal will be looked up. Any operating system supported by Dcoker Machine's provisioner.
        :param output_limit: Maximum build log size in kilobytes. Default is 4096 (4MB). Default: 52428800 (50GB)
        :param role: Optionally pass an IAM role, that get's assigned to the EC2 runner instances.

        :link: GitlabRunnerAutoscalingProps
        '''
        if isinstance(docker, dict):
            docker = DockerConfiguration(**docker)
        if isinstance(machine, dict):
            machine = MachineConfiguration(**machine)
        self._values: typing.Dict[str, typing.Any] = {}
        if autoscaling is not None:
            self._values["autoscaling"] = autoscaling
        if docker is not None:
            self._values["docker"] = docker
        if environment is not None:
            self._values["environment"] = environment
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if limit is not None:
            self._values["limit"] = limit
        if machine is not None:
            self._values["machine"] = machine
        if machine_image is not None:
            self._values["machine_image"] = machine_image
        if output_limit is not None:
            self._values["output_limit"] = output_limit
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def autoscaling(self) -> typing.Optional[typing.List[AutoscalingConfiguration]]:
        '''Optional autoscaling configuration.'''
        result = self._values.get("autoscaling")
        return typing.cast(typing.Optional[typing.List[AutoscalingConfiguration]], result)

    @builtins.property
    def docker(self) -> typing.Optional[DockerConfiguration]:
        '''Optional docker configuration.'''
        result = self._values.get("docker")
        return typing.cast(typing.Optional[DockerConfiguration], result)

    @builtins.property
    def environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Append or overwrite environment variables.

        :default: ["DOCKER_DRIVER=overlay2", "DOCKER_TLS_CERTDIR=/certs"]
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''Instance type for runner EC2 instances.

        It's a combination of a class and size.

        :default: InstanceType.of(InstanceClass.T3, InstanceSize.MICRO)
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def limit(self) -> typing.Optional[jsii.Number]:
        '''Limit how many jobs can be handled concurrently by this registered runner.

        0 (default) means do not limit.

        :default: 10
        '''
        result = self._values.get("limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def machine(self) -> typing.Optional["MachineConfiguration"]:
        '''Optional docker machine configuration.'''
        result = self._values.get("machine")
        return typing.cast(typing.Optional["MachineConfiguration"], result)

    @builtins.property
    def machine_image(self) -> typing.Optional[aws_cdk.aws_ec2.IMachineImage]:
        '''An Amazon Machine Image ID for the Runners EC2 instances.

        If empty the latest Ubuntu 20.04 focal will be looked up.

        Any operating system supported by Dcoker Machine's provisioner.

        :see: https://gitlab.com/gitlab-org/ci-cd/docker-machine/-/tree/main/libmachine/provision
        '''
        result = self._values.get("machine_image")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IMachineImage], result)

    @builtins.property
    def output_limit(self) -> typing.Optional[jsii.Number]:
        '''Maximum build log size in kilobytes.

        Default is 4096 (4MB).

        :default: 52428800 (50GB)
        '''
        result = self._values.get("output_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Optionally pass an IAM role, that get's assigned to the EC2 runner instances.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabRunnerAutoscalingRunnerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.GitlabRunnerAutoscalingRunners",
    jsii_struct_bases=[],
    name_mapping={
        "instance_profile": "instanceProfile",
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "role": "role",
        "security_group": "securityGroup",
        "security_group_name": "securityGroupName",
    },
)
class GitlabRunnerAutoscalingRunners:
    def __init__(
        self,
        *,
        instance_profile: aws_cdk.aws_iam.CfnInstanceProfile,
        instance_type: aws_cdk.aws_ec2.InstanceType,
        machine_image: aws_cdk.aws_ec2.IMachineImage,
        role: aws_cdk.aws_iam.IRole,
        security_group: aws_cdk.aws_ec2.ISecurityGroup,
        security_group_name: builtins.str,
    ) -> None:
        '''
        :param instance_profile: 
        :param instance_type: 
        :param machine_image: 
        :param role: 
        :param security_group: 
        :param security_group_name: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_profile": instance_profile,
            "instance_type": instance_type,
            "machine_image": machine_image,
            "role": role,
            "security_group": security_group,
            "security_group_name": security_group_name,
        }

    @builtins.property
    def instance_profile(self) -> aws_cdk.aws_iam.CfnInstanceProfile:
        result = self._values.get("instance_profile")
        assert result is not None, "Required property 'instance_profile' is missing"
        return typing.cast(aws_cdk.aws_iam.CfnInstanceProfile, result)

    @builtins.property
    def instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(aws_cdk.aws_ec2.InstanceType, result)

    @builtins.property
    def machine_image(self) -> aws_cdk.aws_ec2.IMachineImage:
        result = self._values.get("machine_image")
        assert result is not None, "Required property 'machine_image' is missing"
        return typing.cast(aws_cdk.aws_ec2.IMachineImage, result)

    @builtins.property
    def role(self) -> aws_cdk.aws_iam.IRole:
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(aws_cdk.aws_iam.IRole, result)

    @builtins.property
    def security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        result = self._values.get("security_group")
        assert result is not None, "Required property 'security_group' is missing"
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, result)

    @builtins.property
    def security_group_name(self) -> builtins.str:
        result = self._values.get("security_group_name")
        assert result is not None, "Required property 'security_group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabRunnerAutoscalingRunners(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.GlobalConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "check_interval": "checkInterval",
        "concurrent": "concurrent",
        "log_format": "logFormat",
        "log_level": "logLevel",
    },
)
class GlobalConfiguration:
    def __init__(
        self,
        *,
        check_interval: typing.Optional[jsii.Number] = None,
        concurrent: typing.Optional[jsii.Number] = None,
        log_format: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''You can change the behavior of GitLab Runner and of individual registered runners.

        This imitates the structure of Gitlab Runner advanced configuration that originally is set with config.toml file.

        :param check_interval: The check_interval option defines how often the runner should check GitLab for new jobs| in seconds. Default: 0
        :param concurrent: The limit of the jobs that can be run concurrently across all runners (concurrent). Default: 10
        :param log_format: The log format. Default: "runner"
        :param log_level: The log_level. Default: "info"

        :see: https://docs.gitlab.com/runner/configuration/advanced-configuration.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if check_interval is not None:
            self._values["check_interval"] = check_interval
        if concurrent is not None:
            self._values["concurrent"] = concurrent
        if log_format is not None:
            self._values["log_format"] = log_format
        if log_level is not None:
            self._values["log_level"] = log_level

    @builtins.property
    def check_interval(self) -> typing.Optional[jsii.Number]:
        '''The check_interval option defines how often the runner should check GitLab for new jobs| in seconds.

        :default: 0
        '''
        result = self._values.get("check_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def concurrent(self) -> typing.Optional[jsii.Number]:
        '''The limit of the jobs that can be run concurrently across all runners (concurrent).

        :default: 10
        '''
        result = self._values.get("concurrent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_format(self) -> typing.Optional[builtins.str]:
        '''The log format.

        :default: "runner"
        '''
        result = self._values.get("log_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        '''The log_level.

        :default: "info"
        '''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GlobalConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.MachineConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "idle_count": "idleCount",
        "idle_time": "idleTime",
        "machine_driver": "machineDriver",
        "machine_name": "machineName",
        "machine_options": "machineOptions",
        "max_builds": "maxBuilds",
    },
)
class MachineConfiguration:
    def __init__(
        self,
        *,
        idle_count: typing.Optional[jsii.Number] = None,
        idle_time: typing.Optional[jsii.Number] = None,
        machine_driver: typing.Optional[builtins.str] = None,
        machine_name: typing.Optional[builtins.str] = None,
        machine_options: typing.Optional["MachineOptions"] = None,
        max_builds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param idle_count: Number of machines that need to be created and waiting in Idle state. Default: 0
        :param idle_time: Time (in seconds) for machine to be in Idle state before it is removed. Default: 300
        :param machine_driver: Docker Machine driver. Default: "amazonec2"
        :param machine_name: Default: "gitlab-runner"
        :param machine_options: Docker Machine options passed to the Docker Machine driver.
        :param max_builds: Maximum job (build) count before machine is removed. Default: 20
        '''
        if isinstance(machine_options, dict):
            machine_options = MachineOptions(**machine_options)
        self._values: typing.Dict[str, typing.Any] = {}
        if idle_count is not None:
            self._values["idle_count"] = idle_count
        if idle_time is not None:
            self._values["idle_time"] = idle_time
        if machine_driver is not None:
            self._values["machine_driver"] = machine_driver
        if machine_name is not None:
            self._values["machine_name"] = machine_name
        if machine_options is not None:
            self._values["machine_options"] = machine_options
        if max_builds is not None:
            self._values["max_builds"] = max_builds

    @builtins.property
    def idle_count(self) -> typing.Optional[jsii.Number]:
        '''Number of machines that need to be created and waiting in Idle state.

        :default: 0
        '''
        result = self._values.get("idle_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def idle_time(self) -> typing.Optional[jsii.Number]:
        '''Time (in seconds) for machine to be in Idle state before it is removed.

        :default: 300
        '''
        result = self._values.get("idle_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def machine_driver(self) -> typing.Optional[builtins.str]:
        '''Docker Machine driver.

        :default: "amazonec2"
        '''
        result = self._values.get("machine_driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def machine_name(self) -> typing.Optional[builtins.str]:
        '''
        :default: "gitlab-runner"
        '''
        result = self._values.get("machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def machine_options(self) -> typing.Optional["MachineOptions"]:
        '''Docker Machine options passed to the Docker Machine driver.'''
        result = self._values.get("machine_options")
        return typing.cast(typing.Optional["MachineOptions"], result)

    @builtins.property
    def max_builds(self) -> typing.Optional[jsii.Number]:
        '''Maximum job (build) count before machine is removed.

        :default: 20
        '''
        result = self._values.get("max_builds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MachineConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.MachineOptions",
    jsii_struct_bases=[],
    name_mapping={
        "ami": "ami",
        "block_duration_minutes": "blockDurationMinutes",
        "iam_instance_profile": "iamInstanceProfile",
        "instance_type": "instanceType",
        "region": "region",
        "request_spot_instance": "requestSpotInstance",
        "security_group": "securityGroup",
        "spot_price": "spotPrice",
        "subnet_id": "subnetId",
        "use_private_address": "usePrivateAddress",
        "vpc_id": "vpcId",
        "zone": "zone",
    },
)
class MachineOptions:
    def __init__(
        self,
        *,
        ami: typing.Optional[builtins.str] = None,
        block_duration_minutes: typing.Optional[jsii.Number] = None,
        iam_instance_profile: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        request_spot_instance: typing.Optional[builtins.bool] = None,
        security_group: typing.Optional[builtins.str] = None,
        spot_price: typing.Optional[jsii.Number] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        use_private_address: typing.Optional[builtins.bool] = None,
        vpc_id: typing.Optional[builtins.str] = None,
        zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ami: 
        :param block_duration_minutes: The amazonec2-block-duration-minutes parameter. AWS spot instance duration in minutes (60, 120, 180, 240, 300, or 360).
        :param iam_instance_profile: 
        :param instance_type: 
        :param region: 
        :param request_spot_instance: The amazonec2-request-spot-instance parameter. Whether or not to request spot instances. Default: true
        :param security_group: The SecurityGroup's GroupName, not the GroupId.
        :param spot_price: The amazonec2-spot-price parameter. The bidding price for spot instances. Default: 0.03
        :param subnet_id: 
        :param use_private_address: 
        :param vpc_id: 
        :param zone: Extract the availabilityZone last character for the needs of gitlab configuration.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if ami is not None:
            self._values["ami"] = ami
        if block_duration_minutes is not None:
            self._values["block_duration_minutes"] = block_duration_minutes
        if iam_instance_profile is not None:
            self._values["iam_instance_profile"] = iam_instance_profile
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if region is not None:
            self._values["region"] = region
        if request_spot_instance is not None:
            self._values["request_spot_instance"] = request_spot_instance
        if security_group is not None:
            self._values["security_group"] = security_group
        if spot_price is not None:
            self._values["spot_price"] = spot_price
        if subnet_id is not None:
            self._values["subnet_id"] = subnet_id
        if use_private_address is not None:
            self._values["use_private_address"] = use_private_address
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id
        if zone is not None:
            self._values["zone"] = zone

    @builtins.property
    def ami(self) -> typing.Optional[builtins.str]:
        result = self._values.get("ami")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_duration_minutes(self) -> typing.Optional[jsii.Number]:
        '''The amazonec2-block-duration-minutes parameter.

        AWS spot instance duration in minutes (60, 120, 180, 240, 300, or 360).

        :see: https://docs.gitlab.com/runner/configuration/runner_autoscale_aws/#cutting-down-costs-with-amazon-ec2-spot-instances
        '''
        result = self._values.get("block_duration_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def iam_instance_profile(self) -> typing.Optional[builtins.str]:
        result = self._values.get("iam_instance_profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[builtins.str]:
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_spot_instance(self) -> typing.Optional[builtins.bool]:
        '''The amazonec2-request-spot-instance parameter.

        Whether or not to request spot instances.

        :default: true

        :see: https://aws.amazon.com/ec2/spot/
        '''
        result = self._values.get("request_spot_instance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_group(self) -> typing.Optional[builtins.str]:
        '''The SecurityGroup's GroupName, not the GroupId.'''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spot_price(self) -> typing.Optional[jsii.Number]:
        '''The amazonec2-spot-price parameter.

        The bidding price for spot instances.

        :default: 0.03

        :see: https://aws.amazon.com/ec2/spot/pricing/
        '''
        result = self._values.get("spot_price")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def subnet_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("subnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_private_address(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("use_private_address")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zone(self) -> typing.Optional[builtins.str]:
        '''Extract the availabilityZone last character for the needs of gitlab configuration.

        :see: https://docs.gitlab.com/runners/configuration/runners_autoscale_aws/#the-runnerssmachine-section
        '''
        result = self._values.get("zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MachineOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Network(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.Network",
):
    '''Network settings for the manager and runners.

    All EC2 instances should belong to the same subnet, availability zone and vpc.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Stack,
        id: builtins.str,
        *,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param subnet_selection: The GitLab Runner's subnets. It should be either public or private. If more then subnet is selected, then the first found (private) subnet will be used.
        :param vpc: If no existing VPC is provided, a default Vpc will be created.
        '''
        props = NetworkProps(subnet_selection=subnet_selection, vpc=vpc)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnet")
    def subnet(self) -> aws_cdk.aws_ec2.ISubnet:
        return typing.cast(aws_cdk.aws_ec2.ISubnet, jsii.get(self, "subnet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.NetworkProps",
    jsii_struct_bases=[],
    name_mapping={"subnet_selection": "subnetSelection", "vpc": "vpc"},
)
class NetworkProps:
    def __init__(
        self,
        *,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param subnet_selection: The GitLab Runner's subnets. It should be either public or private. If more then subnet is selected, then the first found (private) subnet will be used.
        :param vpc: If no existing VPC is provided, a default Vpc will be created.
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = aws_cdk.aws_ec2.SubnetSelection(**subnet_selection)
        self._values: typing.Dict[str, typing.Any] = {}
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def subnet_selection(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''The GitLab Runner's subnets.

        It should be either public or private. If more then subnet is selected, then the first found (private) subnet will be used.

        :see: https://docs.aws.amazon.com/cdk/api/latest/docs/
        :aws-cdk_aws-ec2:

        .SubnetSelection.html

        A network is considered private, if

        - tagged by 'aws-cdk:subnet-type'
        - doesn't route to an Internet Gateway (not public)
        - has an Nat Gateway
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''If no existing VPC is provided, a default Vpc will be created.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.RunnerConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "builds_dir": "buildsDir",
        "cache_dir": "cacheDir",
        "clone_url": "cloneUrl",
        "debug_trace_disabled": "debugTraceDisabled",
        "environment": "environment",
        "executor": "executor",
        "limit": "limit",
        "name": "name",
        "output_limit": "outputLimit",
        "post_build_script": "postBuildScript",
        "pre_build_script": "preBuildScript",
        "pre_clone_script": "preCloneScript",
        "referees": "referees",
        "request_concurrency": "requestConcurrency",
        "shell": "shell",
        "tls_ca_file": "tlsCaFile",
        "tls_cert_file": "tlsCertFile",
        "tls_key_file": "tlsKeyFile",
        "token": "token",
        "url": "url",
    },
)
class RunnerConfiguration:
    def __init__(
        self,
        *,
        builds_dir: typing.Optional[builtins.str] = None,
        cache_dir: typing.Optional[builtins.str] = None,
        clone_url: typing.Optional[builtins.str] = None,
        debug_trace_disabled: typing.Optional[builtins.bool] = None,
        environment: typing.Optional[typing.Sequence[builtins.str]] = None,
        executor: typing.Optional[builtins.str] = None,
        limit: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        output_limit: typing.Optional[jsii.Number] = None,
        post_build_script: typing.Optional[builtins.str] = None,
        pre_build_script: typing.Optional[builtins.str] = None,
        pre_clone_script: typing.Optional[builtins.str] = None,
        referees: typing.Optional[builtins.str] = None,
        request_concurrency: typing.Optional[jsii.Number] = None,
        shell: typing.Optional[builtins.str] = None,
        tls_ca_file: typing.Optional[builtins.str] = None,
        tls_cert_file: typing.Optional[builtins.str] = None,
        tls_key_file: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param builds_dir: Absolute path to a directory where builds are stored in the context of the selected executor. For example, locally, Docker, or SSH.
        :param cache_dir: Absolute path to a directory where build caches are stored in context of selected executor. For example, locally, Docker, or SSH. If the docker executor is used, this directory needs to be included in its volumes parameter.
        :param clone_url: Overwrite the URL for the GitLab instance. Used only if the runner can’t connect to the GitLab URL.
        :param debug_trace_disabled: Disables the CI_DEBUG_TRACE feature. When set to true, then debug log (trace) remains disabled, even if CI_DEBUG_TRACE is set to true by the user.
        :param environment: Append or overwrite environment variables. Default: ["DOCKER_DRIVER=overlay2", "DOCKER_TLS_CERTDIR=/certs"]
        :param executor: Select how a project should be built. Default: "docker+machine"
        :param limit: Limit how many jobs can be handled concurrently by this registered runner. 0 (default) means do not limit. Default: 10
        :param name: The runner’s description. Informational only. Default: "gitlab-runner"
        :param output_limit: Maximum build log size in kilobytes. Default is 4096 (4MB). Default: 52428800 (50GB)
        :param post_build_script: Commands to be executed on the runner just after executing the build, but before executing after_script. To insert multiple commands, use a (triple-quoted) multi-line string or \\n character.
        :param pre_build_script: Commands to be executed on the runner after cloning the Git repository, but before executing the build. To insert multiple commands, use a (triple-quoted) multi-line string or \\n character.
        :param pre_clone_script: Commands to be executed on the runner before cloning the Git repository. Use it to adjust the Git client configuration first, for example. To insert multiple commands, use a (triple-quoted) multi-line string or \\n character.
        :param referees: Extra job monitoring workers that pass their results as job artifacts to GitLab.
        :param request_concurrency: Limit number of concurrent requests for new jobs from GitLab. Default is 1.
        :param shell: Name of shell to generate the script. Default value is platform dependent.
        :param tls_ca_file: When using HTTPS, file that contains the certificates to verify the peer. See Self-signed certificates or custom Certification Authorities documentation.
        :param tls_cert_file: When using HTTPS, file that contains the certificate to authenticate with the peer.
        :param tls_key_file: When using HTTPS, file that contains the private key to authenticate with the peer.
        :param token: The runner’s authentication token, which is obtained during runner registration. Not the same as the registration token.
        :param url: GitLab instance URL. Default: "https://gitlab.com"
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if builds_dir is not None:
            self._values["builds_dir"] = builds_dir
        if cache_dir is not None:
            self._values["cache_dir"] = cache_dir
        if clone_url is not None:
            self._values["clone_url"] = clone_url
        if debug_trace_disabled is not None:
            self._values["debug_trace_disabled"] = debug_trace_disabled
        if environment is not None:
            self._values["environment"] = environment
        if executor is not None:
            self._values["executor"] = executor
        if limit is not None:
            self._values["limit"] = limit
        if name is not None:
            self._values["name"] = name
        if output_limit is not None:
            self._values["output_limit"] = output_limit
        if post_build_script is not None:
            self._values["post_build_script"] = post_build_script
        if pre_build_script is not None:
            self._values["pre_build_script"] = pre_build_script
        if pre_clone_script is not None:
            self._values["pre_clone_script"] = pre_clone_script
        if referees is not None:
            self._values["referees"] = referees
        if request_concurrency is not None:
            self._values["request_concurrency"] = request_concurrency
        if shell is not None:
            self._values["shell"] = shell
        if tls_ca_file is not None:
            self._values["tls_ca_file"] = tls_ca_file
        if tls_cert_file is not None:
            self._values["tls_cert_file"] = tls_cert_file
        if tls_key_file is not None:
            self._values["tls_key_file"] = tls_key_file
        if token is not None:
            self._values["token"] = token
        if url is not None:
            self._values["url"] = url

    @builtins.property
    def builds_dir(self) -> typing.Optional[builtins.str]:
        '''Absolute path to a directory where builds are stored in the context of the selected executor.

        For example, locally, Docker, or SSH.
        '''
        result = self._values.get("builds_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_dir(self) -> typing.Optional[builtins.str]:
        '''Absolute path to a directory where build caches are stored in context of selected executor.

        For example, locally, Docker, or SSH. If the docker executor is used, this directory needs to be included in its volumes parameter.
        '''
        result = self._values.get("cache_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def clone_url(self) -> typing.Optional[builtins.str]:
        '''Overwrite the URL for the GitLab instance.

        Used only if the runner can’t connect to the GitLab URL.
        '''
        result = self._values.get("clone_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def debug_trace_disabled(self) -> typing.Optional[builtins.bool]:
        '''Disables the CI_DEBUG_TRACE feature.

        When set to true, then debug log (trace) remains disabled, even if CI_DEBUG_TRACE is set to true by the user.
        '''
        result = self._values.get("debug_trace_disabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def environment(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Append or overwrite environment variables.

        :default: ["DOCKER_DRIVER=overlay2", "DOCKER_TLS_CERTDIR=/certs"]
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def executor(self) -> typing.Optional[builtins.str]:
        '''Select how a project should be built.

        :default: "docker+machine"
        '''
        result = self._values.get("executor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def limit(self) -> typing.Optional[jsii.Number]:
        '''Limit how many jobs can be handled concurrently by this registered runner.

        0 (default) means do not limit.

        :default: 10
        '''
        result = self._values.get("limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The runner’s description.

        Informational only.

        :default: "gitlab-runner"
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_limit(self) -> typing.Optional[jsii.Number]:
        '''Maximum build log size in kilobytes.

        Default is 4096 (4MB).

        :default: 52428800 (50GB)
        '''
        result = self._values.get("output_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def post_build_script(self) -> typing.Optional[builtins.str]:
        '''Commands to be executed on the runner just after executing the build, but before executing after_script.

        To insert multiple commands, use a (triple-quoted) multi-line string or \\n character.
        '''
        result = self._values.get("post_build_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_build_script(self) -> typing.Optional[builtins.str]:
        '''Commands to be executed on the runner after cloning the Git repository, but before executing the build.

        To insert multiple commands, use a (triple-quoted) multi-line string or \\n character.
        '''
        result = self._values.get("pre_build_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_clone_script(self) -> typing.Optional[builtins.str]:
        '''Commands to be executed on the runner before cloning the Git repository.

        Use it to adjust the Git client configuration first, for example. To insert multiple commands, use a (triple-quoted) multi-line string or \\n character.
        '''
        result = self._values.get("pre_clone_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def referees(self) -> typing.Optional[builtins.str]:
        '''Extra job monitoring workers that pass their results as job artifacts to GitLab.'''
        result = self._values.get("referees")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_concurrency(self) -> typing.Optional[jsii.Number]:
        '''Limit number of concurrent requests for new jobs from GitLab.

        Default is 1.
        '''
        result = self._values.get("request_concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def shell(self) -> typing.Optional[builtins.str]:
        '''Name of shell to generate the script.

        Default value is platform dependent.
        '''
        result = self._values.get("shell")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_ca_file(self) -> typing.Optional[builtins.str]:
        '''When using HTTPS, file that contains the certificates to verify the peer.

        See Self-signed certificates or custom Certification Authorities documentation.
        '''
        result = self._values.get("tls_ca_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_cert_file(self) -> typing.Optional[builtins.str]:
        '''When using HTTPS, file that contains the certificate to authenticate with the peer.'''
        result = self._values.get("tls_cert_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_key_file(self) -> typing.Optional[builtins.str]:
        '''When using HTTPS, file that contains the private key to authenticate with the peer.'''
        result = self._values.get("tls_key_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''The runner’s authentication token, which is obtained during runner registration.

        Not the same as the registration token.
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''GitLab instance URL.

        :default: "https://gitlab.com"
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RunnerConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-autoscaling-gitlab-runner.GitlabRunnerAutoscalingProps",
    jsii_struct_bases=[GlobalConfiguration],
    name_mapping={
        "check_interval": "checkInterval",
        "concurrent": "concurrent",
        "log_format": "logFormat",
        "log_level": "logLevel",
        "gitlab_token": "gitlabToken",
        "cache": "cache",
        "gitlab_url": "gitlabUrl",
        "manager": "manager",
        "network": "network",
        "runners": "runners",
    },
)
class GitlabRunnerAutoscalingProps(GlobalConfiguration):
    def __init__(
        self,
        *,
        check_interval: typing.Optional[jsii.Number] = None,
        concurrent: typing.Optional[jsii.Number] = None,
        log_format: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        gitlab_token: builtins.str,
        cache: typing.Optional[GitlabRunnerAutoscalingCacheProps] = None,
        gitlab_url: typing.Optional[builtins.str] = None,
        manager: typing.Optional[GitlabRunnerAutoscalingManagerProps] = None,
        network: typing.Optional[NetworkProps] = None,
        runners: typing.Optional[GitlabRunnerAutoscalingRunnerProps] = None,
    ) -> None:
        '''Properties of the Gitlab Runner.

        You have to provide at least the GitLab's Runner's authentication token.

        :param check_interval: The check_interval option defines how often the runner should check GitLab for new jobs| in seconds. Default: 0
        :param concurrent: The limit of the jobs that can be run concurrently across all runners (concurrent). Default: 10
        :param log_format: The log format. Default: "runner"
        :param log_level: The log_level. Default: "info"
        :param gitlab_token: The GitLab Runner’s authentication token, which is obtained during runner registration.
        :param cache: 
        :param gitlab_url: GitLab instance URL. Default: "https://gitlab.com"
        :param manager: The manager EC2 instance configuration. If not set, the defaults will be used.
        :param network: The network configuration for the Runner. If not set, the defaults will be used.
        :param runners: 
        '''
        if isinstance(cache, dict):
            cache = GitlabRunnerAutoscalingCacheProps(**cache)
        if isinstance(manager, dict):
            manager = GitlabRunnerAutoscalingManagerProps(**manager)
        if isinstance(network, dict):
            network = NetworkProps(**network)
        if isinstance(runners, dict):
            runners = GitlabRunnerAutoscalingRunnerProps(**runners)
        self._values: typing.Dict[str, typing.Any] = {
            "gitlab_token": gitlab_token,
        }
        if check_interval is not None:
            self._values["check_interval"] = check_interval
        if concurrent is not None:
            self._values["concurrent"] = concurrent
        if log_format is not None:
            self._values["log_format"] = log_format
        if log_level is not None:
            self._values["log_level"] = log_level
        if cache is not None:
            self._values["cache"] = cache
        if gitlab_url is not None:
            self._values["gitlab_url"] = gitlab_url
        if manager is not None:
            self._values["manager"] = manager
        if network is not None:
            self._values["network"] = network
        if runners is not None:
            self._values["runners"] = runners

    @builtins.property
    def check_interval(self) -> typing.Optional[jsii.Number]:
        '''The check_interval option defines how often the runner should check GitLab for new jobs| in seconds.

        :default: 0
        '''
        result = self._values.get("check_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def concurrent(self) -> typing.Optional[jsii.Number]:
        '''The limit of the jobs that can be run concurrently across all runners (concurrent).

        :default: 10
        '''
        result = self._values.get("concurrent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_format(self) -> typing.Optional[builtins.str]:
        '''The log format.

        :default: "runner"
        '''
        result = self._values.get("log_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        '''The log_level.

        :default: "info"
        '''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlab_token(self) -> builtins.str:
        '''The GitLab Runner’s authentication token, which is obtained during runner registration.

        :see: https://docs.gitlab.com/ee/api/runners.html#registration-and-authentication-tokens
        '''
        result = self._values.get("gitlab_token")
        assert result is not None, "Required property 'gitlab_token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cache(self) -> typing.Optional[GitlabRunnerAutoscalingCacheProps]:
        result = self._values.get("cache")
        return typing.cast(typing.Optional[GitlabRunnerAutoscalingCacheProps], result)

    @builtins.property
    def gitlab_url(self) -> typing.Optional[builtins.str]:
        '''GitLab instance URL.

        :default: "https://gitlab.com"
        '''
        result = self._values.get("gitlab_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def manager(self) -> typing.Optional[GitlabRunnerAutoscalingManagerProps]:
        '''The manager EC2 instance configuration.

        If not set, the defaults will be used.

        :link: GitlabRunnerAutoscalingManagerProps
        '''
        result = self._values.get("manager")
        return typing.cast(typing.Optional[GitlabRunnerAutoscalingManagerProps], result)

    @builtins.property
    def network(self) -> typing.Optional[NetworkProps]:
        '''The network configuration for the Runner.

        If not set, the defaults will be used.

        :link: NetworkProps
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[NetworkProps], result)

    @builtins.property
    def runners(self) -> typing.Optional[GitlabRunnerAutoscalingRunnerProps]:
        result = self._values.get("runners")
        return typing.cast(typing.Optional[GitlabRunnerAutoscalingRunnerProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabRunnerAutoscalingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AutoscalingConfiguration",
    "Cache",
    "CacheConfiguration",
    "CacheProps",
    "CacheS3Configuration",
    "ConfigurationMapper",
    "ConfigurationMapperProps",
    "DockerConfiguration",
    "GitlabRunnerAutoscaling",
    "GitlabRunnerAutoscalingCacheProps",
    "GitlabRunnerAutoscalingManager",
    "GitlabRunnerAutoscalingManagerProps",
    "GitlabRunnerAutoscalingProps",
    "GitlabRunnerAutoscalingRunnerProps",
    "GitlabRunnerAutoscalingRunners",
    "GlobalConfiguration",
    "MachineConfiguration",
    "MachineOptions",
    "Network",
    "NetworkProps",
    "RunnerConfiguration",
]

publication.publish()
