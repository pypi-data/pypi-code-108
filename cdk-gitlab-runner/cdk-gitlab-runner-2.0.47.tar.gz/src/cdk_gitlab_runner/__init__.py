'''
[![NPM version](https://badge.fury.io/js/cdk-gitlab-runner.svg)](https://badge.fury.io/js/cdk-gitlab-runner)
[![PyPI version](https://badge.fury.io/py/cdk-gitlab-runner.svg)](https://badge.fury.io/py/cdk-gitlab-runner)
![Release](https://github.com/neilkuan/cdk-gitlab-runner/workflows/Release/badge.svg)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/cdk-gitlab-runner?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/cdk-gitlab-runner?label=pypi&color=blue)

![](https://img.shields.io/badge/iam_role_self-enable-green=?style=plastic&logo=appveyor)
![](https://img.shields.io/badge/vpc_self-enable-green=?style=plastic&logo=appveyor)
![](https://img.shields.io/badge/gitlab_url-customize-green=?style=plastic&logo=appveyor)
![](https://img.shields.io/badge/spotfleet-runner-green=?style=plastic&logo=appveyor)

# Welcome to `cdk-gitlab-runner`

Use AWS CDK to create gitlab runner, and use [gitlab runner](https://gitlab.com/gitlab-org/gitlab-runner) to help you execute your Gitlab Pipeline Job.

> GitLab Runner is the open source project that is used to run your CI/CD jobs and send the results back to GitLab. [(source repo)](https://gitlab.com/gitlab-org/gitlab-runner)

## Why

Gitlab provides [400 minutes per month for each free user](https://about.gitlab.com/pricing/), hosted Gitlab Runner to execute your gitlab pipeline job.That's pretty good and users don't need to manage gitlab runner. If it is just a simple ci job for test 400, it may be enough.
But what if you want to deploy to your AWS production environment through pipeline job?
Is there any security consideration for using the hosted gitlab runner?!

But creating Gitlab Runner is not that simple, so I created this OSS so that you can quickly create Gitlab Runner and delete your Gitlab Runner via AWS CDK.
It will be used with AWS IAM Role, so you don't need to put AKSK in Gitlab environment variables.

![](./image/cdk-gitlab-runner.png)

## Note

### Default will help you generate below services:

* VPC

  * Public Subnet (2)
* EC2 (1 T3.micro)

## Before start you need gitlab runner token in your `gitlab project` or `gitlab group`

### In Group

Group > Settings > CI/CD
![group](image/group_runner_page.png)

### In Project

Project > Settings > CI/CD > Runners
![project](image/project_runner_page.png)

## Usage

Replace your gitlab runner token in `$GITLABTOKEN`

## Install

Use the npm dist tag to opt in CDKv1 or CDKv2:

```bash
// for CDKv2
npm install cdk-gitlab-runner
or
npm install cdk-gitlab-runner@latest

// for CDKv1
npm install cdk-gitlab-runner@cdkv1
```

## 💡💡💡 please click [here](https://github.com/neilkuan/cdk-gitlab-runner/tree/cdkv1#readme), if you are using aws-cdk v1.x.x version.💡💡💡

### Instance Type

```python
import { GitlabContainerRunner } from 'cdk-gitlab-runner';

// If want change instance type to t3.large .
new GitlabContainerRunner(this, 'runner-instance', { gitlabtoken: '$GITLABTOKEN', ec2type:'t3.large' });
// OR
// Just create a gitlab runner , by default instance type is t3.micro .
import { GitlabContainerRunner } from 'cdk-gitlab-runner';

new GitlabContainerRunner(this, 'runner-instance', { gitlabtoken: '$GITLABTOKEN' });})
```

### Gitlab Server Customize Url .

If you want change what you want tag name .

```python
// If you want change  what  your self Gitlab Server Url .
import { GitlabContainerRunner } from 'cdk-gitlab-runner';

new GitlabContainerRunner(this, 'runner-instance-change-tag', {
  gitlabtoken: '$GITLABTOKEN',
  gitlaburl: 'https://gitlab.my.com/',
});
```

### Tags

If you want change what you want tag name .

```python
// If you want change  what  you want tag name .
import { GitlabContainerRunner } from 'cdk-gitlab-runner';

new GitlabContainerRunner(this, 'runner-instance-change-tag', {
  gitlabtoken: '$GITLABTOKEN',
  tags: ['aa', 'bb', 'cc'],
});
```

### IAM Policy

If you want add runner other IAM Policy like s3-readonly-access.

```python
// If you want add runner other IAM Policy like s3-readonly-access.
import { GitlabContainerRunner } from 'cdk-gitlab-runner';
import { ManagedPolicy } from 'aws-cdk-lib/aws-iam';

const runner = new GitlabContainerRunner(this, 'runner-instance-add-policy', {
  gitlabtoken: '$GITLABTOKEN',
  tags: ['aa', 'bb', 'cc'],
});
runner.runnerRole.addManagedPolicy(
  ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'),
);
```

### Security Group

If you want add runner other SG Ingress .

```python
// If you want add runner other SG Ingress .
import { GitlabContainerRunner } from 'cdk-gitlab-runner';
import { Port, Peer } from 'aws-cdk-lib/aws-ec2';

const runner = new GitlabContainerRunner(this, 'runner-add-SG-ingress', {
  gitlabtoken: 'GITLABTOKEN',
  tags: ['aa', 'bb', 'cc'],
});

// you can add ingress in your runner SG .
runner.defaultRunnerSG.connections.allowFrom(
  Peer.ipv4('0.0.0.0/0'),
  Port.tcp(80),
);
```

### Use self VPC

> 2020/06/27 , you can use your self exist VPC or new VPC , but please check your `vpc public Subnet` Auto-assign public IPv4 address must be Yes ,or `vpc private Subnet` route table associated `nat gateway` .

```python
import { GitlabContainerRunner } from 'cdk-gitlab-runner';
import { Port, Peer, Vpc, SubnetType } from 'aws-cdk-lib/aws-ec2';
import { ManagedPolicy } from 'aws-cdk-lib/aws-iam';

const newvpc = new Vpc(stack, 'VPC', {
  cidr: '10.1.0.0/16',
  maxAzs: 2,
  subnetConfiguration: [
    {
      cidrMask: 26,
      name: 'RunnerVPC',
      subnetType: SubnetType.PUBLIC,
    },
  ],
  natGateways: 0,
});

const runner = new GitlabContainerRunner(this, 'testing', {
  gitlabtoken: '$GITLABTOKEN',
  ec2type: 't3.small',
  selfvpc: newvpc,
});
```

### Use your self exist role

> 2020/06/27 , you can use your self exist role assign to runner

```python
import { GitlabContainerRunner } from 'cdk-gitlab-runner';
import { Port, Peer } from 'aws-cdk-lib/aws-ec2';
import { ManagedPolicy, Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam';

const role = new Role(this, 'runner-role', {
  assumedBy: new ServicePrincipal('ec2.amazonaws.com'),
  description: 'For Gitlab EC2 Runner Test Role',
  roleName: 'TestRole',
});

const runner = new GitlabContainerRunner(stack, 'testing', {
  gitlabtoken: '$GITLAB_TOKEN',
  ec2iamrole: role,
});
runner.runnerRole.addManagedPolicy(
  ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'),
);
```

### Custom Gitlab Runner EBS szie

> 2020/08/22 , you can change you want ebs size.

```python
import { GitlabContainerRunner } from 'cdk-gitlab-runner';

new GitlabContainerRunner(stack, 'testing', {
  gitlabtoken: '$GITLAB_TOKEN',
  ebsSize: 50,
});
```

### Control the number of runners with AutoScalingGroup

> 2020/11/25 , you can set the number of runners.

```python
import { GitlabRunnerAutoscaling } from 'cdk-gitlab-runner';

new GitlabRunnerAutoscaling(stack, 'testing', {
  gitlabToken: '$GITLAB_TOKEN',
  minCapacity: 2,
  maxCapacity: 2,
});
```

### Support Spotfleet Gitlab Runner

> 2020/08/27 , you can use spotfleet instance be your gitlab runner,
> after create spotfleet instance will auto output instance id.

```python
import { GitlabContainerRunner, BlockDuration } from 'cdk-gitlab-runner';

const runner = new GitlabContainerRunner(stack, 'testing', {
  gitlabtoken: 'GITLAB_TOKEN',
  ec2type: 't3.large',
  blockDuration: BlockDuration.ONE_HOUR,
  spotFleet: true,
});
// configure the expiration after 1 hours
runner.expireAfter(Duration.hours(1));
```

> 2020/11/19, you setting job runtime bind host volumes.
> see more https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section

```python
import { GitlabContainerRunner, BlockDuration } from 'cdk-gitlab-runner';

const runner = new GitlabContainerRunner(stack, 'testing', {
  gitlabtoken: 'GITLAB_TOKEN',
  ec2type: 't3.large',
  dockerVolumes: [
    {
      hostPath: '/tmp/cache',
      containerPath: '/tmp/cache',
    },
  ],
});
```

## Wait about 6 mins , If success you will see your runner in that page .

![runner](image/group_runner2.png)

#### you can use tag `gitlab` , `runner` , `awscdk` ,

## Example *`gitlab-ci.yaml`*

[gitlab docs see more ...](https://docs.gitlab.com/ee/ci/yaml/README.html)

```yaml
dockerjob:
  image: docker:18.09-dind
  variables:
  tags:
    - runner
    - awscdk
    - gitlab
  variables:
    DOCKER_TLS_CERTDIR: ""
  before_script:
    - docker info
  script:
    - docker info;
    - echo 'test 123';
    - echo 'hello world 1228'
```

### If your want to debug you can go to aws console

# `In your runner region !!!`

## AWS Systems Manager > Session Manager > Start a session

![system manager](image/session.png)

#### click your `runner` and click `start session`

#### in the brower console in put `bash`

```bash
# become to root
sudo -i

# list runner container .
root# docker ps -a

# modify gitlab-runner/config.toml

root# cd /home/ec2-user/.gitlab-runner/ && ls
config.toml

```

## :clap:  Supporters

[![Stargazers repo roster for @neilkuan/cdk-gitlab-runner](https://reporoster.com/stars/neilkuan/cdk-gitlab-runner)](https://github.com/neilkuan/cdk-gitlab-runner/stargazers)
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
import aws_cdk.aws_autoscaling
import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_sns
import constructs


@jsii.enum(jsii_type="cdk-gitlab-runner.BlockDuration")
class BlockDuration(enum.Enum):
    '''(experimental) BlockDuration enum.

    :stability: experimental
    '''

    ONE_HOUR = "ONE_HOUR"
    '''(experimental) one hours.

    :stability: experimental
    '''
    TWO_HOURS = "TWO_HOURS"
    '''(experimental) two hours.

    :stability: experimental
    '''
    THREE_HOURS = "THREE_HOURS"
    '''(experimental) three hours.

    :stability: experimental
    '''
    FOUR_HOURS = "FOUR_HOURS"
    '''(experimental) four hours.

    :stability: experimental
    '''
    FIVE_HOURS = "FIVE_HOURS"
    '''(experimental) five hours.

    :stability: experimental
    '''
    SIX_HOURS = "SIX_HOURS"
    '''(experimental) six hours.

    :stability: experimental
    '''
    SEVEN_HOURS = "SEVEN_HOURS"
    '''(experimental) seven hours.

    :stability: experimental
    '''
    EIGHT_HOURS = "EIGHT_HOURS"
    '''(experimental) eight hours.

    :stability: experimental
    '''
    NINE_HOURS = "NINE_HOURS"
    '''(experimental) nine hours.

    :stability: experimental
    '''
    TEN_HOURS = "TEN_HOURS"
    '''(experimental) ten hours.

    :stability: experimental
    '''
    ELEVEN_HOURS = "ELEVEN_HOURS"
    '''(experimental) eleven hours.

    :stability: experimental
    '''
    TWELVE_HOURS = "TWELVE_HOURS"
    '''(experimental) twelve hours.

    :stability: experimental
    '''
    THIRTEEN_HOURS = "THIRTEEN_HOURS"
    '''(experimental) thirteen hours.

    :stability: experimental
    '''
    FOURTEEN_HOURS = "FOURTEEN_HOURS"
    '''(experimental) fourteen hours.

    :stability: experimental
    '''
    FIFTEEN_HOURS = "FIFTEEN_HOURS"
    '''(experimental) fifteen hours.

    :stability: experimental
    '''
    SIXTEEN_HOURS = "SIXTEEN_HOURS"
    '''(experimental) sixteen hours.

    :stability: experimental
    '''
    SEVENTEEN_HOURS = "SEVENTEEN_HOURS"
    '''(experimental) seventeen hours.

    :stability: experimental
    '''
    EIGHTTEEN_HOURS = "EIGHTTEEN_HOURS"
    '''(experimental) eightteen hours.

    :stability: experimental
    '''
    NINETEEN_HOURS = "NINETEEN_HOURS"
    '''(experimental) nineteen hours.

    :stability: experimental
    '''
    TWENTY_HOURS = "TWENTY_HOURS"
    '''(experimental) twenty hours.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="cdk-gitlab-runner.DockerVolumes",
    jsii_struct_bases=[],
    name_mapping={"container_path": "containerPath", "host_path": "hostPath"},
)
class DockerVolumes:
    def __init__(
        self,
        *,
        container_path: builtins.str,
        host_path: builtins.str,
    ) -> None:
        '''(experimental) Docker Volumes interface.

        :param container_path: (experimental) Job Runtime Container Path Host Path.
        :param host_path: (experimental) EC2 Runner Host Path.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "container_path": container_path,
            "host_path": host_path,
        }

    @builtins.property
    def container_path(self) -> builtins.str:
        '''(experimental) Job Runtime Container Path Host Path.

        :stability: experimental

        Example::

            - /tmp/cahce
            more detail see https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section
        '''
        result = self._values.get("container_path")
        assert result is not None, "Required property 'container_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host_path(self) -> builtins.str:
        '''(experimental) EC2 Runner Host Path.

        :stability: experimental

        Example::

            - /tmp/cahce
            more detail see https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section
        '''
        result = self._values.get("host_path")
        assert result is not None, "Required property 'host_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerVolumes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GitlabContainerRunner(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-gitlab-runner.GitlabContainerRunner",
):
    '''(experimental) GitlabContainerRunner Construct for create a Gitlab Runner.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        gitlabtoken: builtins.str,
        block_duration: typing.Optional[BlockDuration] = None,
        docker_volumes: typing.Optional[typing.Sequence[DockerVolumes]] = None,
        ebs_size: typing.Optional[jsii.Number] = None,
        ec2iamrole: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        ec2type: typing.Optional[builtins.str] = None,
        gitlab_runner_image: typing.Optional[builtins.str] = None,
        gitlaburl: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional["InstanceInterruptionBehavior"] = None,
        key_name: typing.Optional[builtins.str] = None,
        selfvpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        spot_fleet: typing.Optional[builtins.bool] = None,
        tag1: typing.Optional[builtins.str] = None,
        tag2: typing.Optional[builtins.str] = None,
        tag3: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        valid_until: typing.Optional[builtins.str] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param gitlabtoken: (experimental) Gitlab token for the Register Runner . Default: - You must to give the token !!!
        :param block_duration: (experimental) Reservce the Spot Runner instance as spot block with defined duration. Default: - BlockDuration.ONE_HOUR , !!! only support spotfleet runner !!! .
        :param docker_volumes: (experimental) add another Gitlab Container Runner Docker Volumes Path at job runner runtime. more detail see https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section Default: - already mount "/var/run/docker.sock:/var/run/docker.sock"
        :param ebs_size: (experimental) Gitlab Runner instance EBS size . Default: - ebsSize=60
        :param ec2iamrole: (experimental) IAM role for the Gitlab Runner Instance . Default: - new Role for Gitlab Runner Instance , attach AmazonSSMManagedInstanceCore Policy .
        :param ec2type: (experimental) Runner default EC2 instance type. Default: - t3.micro
        :param gitlab_runner_image: (experimental) Image URL of Gitlab Runner. Default: public.ecr.aws/gitlab/gitlab-runner:alpine
        :param gitlaburl: (experimental) Gitlab Runner register url . Default: - gitlaburl='https://gitlab.com/' , please use https://yourgitlab.com/ do not use https://yourgitlab.com
        :param instance_interruption_behavior: (experimental) The behavior when a Spot Runner Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE , !!! only support spotfleet runner !!! .
        :param key_name: (experimental) SSH key name. Default: - no ssh key will be assigned , !!! only support spotfleet runner !!! .
        :param selfvpc: (experimental) VPC for the Gitlab Runner . Default: - new VPC will be created , 1 Vpc , 2 Public Subnet .
        :param spot_fleet: (experimental) Gitlab Runner instance Use Spot Fleet or not ?!. Default: - spotFleet=false
        :param tag1: (deprecated) Gitlab Runner register tag1 . Default: - tag1: gitlab .
        :param tag2: (deprecated) Gitlab Runner register tag2 . Default: - tag2: awscdk .
        :param tag3: (deprecated) Gitlab Runner register tag3 . Default: - tag3: runner .
        :param tags: (experimental) tags for the runner. Default: - ['runner', 'gitlab', 'awscdk']
        :param valid_until: (experimental) the time when the spot fleet allocation expires. Default: - no expiration , !!! only support spotfleet runner !!! .
        :param vpc_subnet: (experimental) VPC subnet for the spot fleet. Default: - public subnet

        :stability: experimental
        '''
        props = GitlabContainerRunnerProps(
            gitlabtoken=gitlabtoken,
            block_duration=block_duration,
            docker_volumes=docker_volumes,
            ebs_size=ebs_size,
            ec2iamrole=ec2iamrole,
            ec2type=ec2type,
            gitlab_runner_image=gitlab_runner_image,
            gitlaburl=gitlaburl,
            instance_interruption_behavior=instance_interruption_behavior,
            key_name=key_name,
            selfvpc=selfvpc,
            spot_fleet=spot_fleet,
            tag1=tag1,
            tag2=tag2,
            tag3=tag3,
            tags=tags,
            valid_until=valid_until,
            vpc_subnet=vpc_subnet,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createUserData")
    def create_user_data(
        self,
        props: "GitlabContainerRunnerProps",
        bucket_name: builtins.str,
    ) -> typing.List[builtins.str]:
        '''
        :param props: -
        :param bucket_name: - the bucketName to put gitlab runner token.

        :return: Array.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "createUserData", [props, bucket_name]))

    @jsii.member(jsii_name="expireAfter")
    def expire_after(self, duration: aws_cdk.Duration) -> None:
        '''(experimental) Add expire time function for spotfleet runner !!! .

        :param duration: - Block duration.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "expireAfter", [duration]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRunnerSG")
    def default_runner_sg(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''(experimental) The EC2 runner's default SecurityGroup.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, jsii.get(self, "defaultRunnerSG"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runnerEc2")
    def runner_ec2(self) -> aws_cdk.aws_ec2.IInstance:
        '''(experimental) This represents a Runner EC2 instance , !!! only support On-demand runner instance !!!

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IInstance, jsii.get(self, "runnerEc2"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runnerRole")
    def runner_role(self) -> aws_cdk.aws_iam.IRole:
        '''(experimental) The IAM role assumed by the Runner instance .

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "runnerRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotFleetInstanceId")
    def spot_fleet_instance_id(self) -> builtins.str:
        '''(experimental) the first instance id in this fleet , !!! only support spotfleet runner !!!

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "spotFleetInstanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="spotFleetRequestId")
    def spot_fleet_request_id(self) -> builtins.str:
        '''(experimental) SpotFleetRequestId for this spot fleet , !!! only support spotfleet runner !!!

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "spotFleetRequestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The EC2 runner's vpc.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-gitlab-runner.GitlabContainerRunnerProps",
    jsii_struct_bases=[],
    name_mapping={
        "gitlabtoken": "gitlabtoken",
        "block_duration": "blockDuration",
        "docker_volumes": "dockerVolumes",
        "ebs_size": "ebsSize",
        "ec2iamrole": "ec2iamrole",
        "ec2type": "ec2type",
        "gitlab_runner_image": "gitlabRunnerImage",
        "gitlaburl": "gitlaburl",
        "instance_interruption_behavior": "instanceInterruptionBehavior",
        "key_name": "keyName",
        "selfvpc": "selfvpc",
        "spot_fleet": "spotFleet",
        "tag1": "tag1",
        "tag2": "tag2",
        "tag3": "tag3",
        "tags": "tags",
        "valid_until": "validUntil",
        "vpc_subnet": "vpcSubnet",
    },
)
class GitlabContainerRunnerProps:
    def __init__(
        self,
        *,
        gitlabtoken: builtins.str,
        block_duration: typing.Optional[BlockDuration] = None,
        docker_volumes: typing.Optional[typing.Sequence[DockerVolumes]] = None,
        ebs_size: typing.Optional[jsii.Number] = None,
        ec2iamrole: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        ec2type: typing.Optional[builtins.str] = None,
        gitlab_runner_image: typing.Optional[builtins.str] = None,
        gitlaburl: typing.Optional[builtins.str] = None,
        instance_interruption_behavior: typing.Optional["InstanceInterruptionBehavior"] = None,
        key_name: typing.Optional[builtins.str] = None,
        selfvpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        spot_fleet: typing.Optional[builtins.bool] = None,
        tag1: typing.Optional[builtins.str] = None,
        tag2: typing.Optional[builtins.str] = None,
        tag3: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        valid_until: typing.Optional[builtins.str] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''(experimental) GitlabContainerRunner Props.

        :param gitlabtoken: (experimental) Gitlab token for the Register Runner . Default: - You must to give the token !!!
        :param block_duration: (experimental) Reservce the Spot Runner instance as spot block with defined duration. Default: - BlockDuration.ONE_HOUR , !!! only support spotfleet runner !!! .
        :param docker_volumes: (experimental) add another Gitlab Container Runner Docker Volumes Path at job runner runtime. more detail see https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section Default: - already mount "/var/run/docker.sock:/var/run/docker.sock"
        :param ebs_size: (experimental) Gitlab Runner instance EBS size . Default: - ebsSize=60
        :param ec2iamrole: (experimental) IAM role for the Gitlab Runner Instance . Default: - new Role for Gitlab Runner Instance , attach AmazonSSMManagedInstanceCore Policy .
        :param ec2type: (experimental) Runner default EC2 instance type. Default: - t3.micro
        :param gitlab_runner_image: (experimental) Image URL of Gitlab Runner. Default: public.ecr.aws/gitlab/gitlab-runner:alpine
        :param gitlaburl: (experimental) Gitlab Runner register url . Default: - gitlaburl='https://gitlab.com/' , please use https://yourgitlab.com/ do not use https://yourgitlab.com
        :param instance_interruption_behavior: (experimental) The behavior when a Spot Runner Instance is interrupted. Default: - InstanceInterruptionBehavior.TERMINATE , !!! only support spotfleet runner !!! .
        :param key_name: (experimental) SSH key name. Default: - no ssh key will be assigned , !!! only support spotfleet runner !!! .
        :param selfvpc: (experimental) VPC for the Gitlab Runner . Default: - new VPC will be created , 1 Vpc , 2 Public Subnet .
        :param spot_fleet: (experimental) Gitlab Runner instance Use Spot Fleet or not ?!. Default: - spotFleet=false
        :param tag1: (deprecated) Gitlab Runner register tag1 . Default: - tag1: gitlab .
        :param tag2: (deprecated) Gitlab Runner register tag2 . Default: - tag2: awscdk .
        :param tag3: (deprecated) Gitlab Runner register tag3 . Default: - tag3: runner .
        :param tags: (experimental) tags for the runner. Default: - ['runner', 'gitlab', 'awscdk']
        :param valid_until: (experimental) the time when the spot fleet allocation expires. Default: - no expiration , !!! only support spotfleet runner !!! .
        :param vpc_subnet: (experimental) VPC subnet for the spot fleet. Default: - public subnet

        :stability: experimental
        '''
        if isinstance(vpc_subnet, dict):
            vpc_subnet = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnet)
        self._values: typing.Dict[str, typing.Any] = {
            "gitlabtoken": gitlabtoken,
        }
        if block_duration is not None:
            self._values["block_duration"] = block_duration
        if docker_volumes is not None:
            self._values["docker_volumes"] = docker_volumes
        if ebs_size is not None:
            self._values["ebs_size"] = ebs_size
        if ec2iamrole is not None:
            self._values["ec2iamrole"] = ec2iamrole
        if ec2type is not None:
            self._values["ec2type"] = ec2type
        if gitlab_runner_image is not None:
            self._values["gitlab_runner_image"] = gitlab_runner_image
        if gitlaburl is not None:
            self._values["gitlaburl"] = gitlaburl
        if instance_interruption_behavior is not None:
            self._values["instance_interruption_behavior"] = instance_interruption_behavior
        if key_name is not None:
            self._values["key_name"] = key_name
        if selfvpc is not None:
            self._values["selfvpc"] = selfvpc
        if spot_fleet is not None:
            self._values["spot_fleet"] = spot_fleet
        if tag1 is not None:
            self._values["tag1"] = tag1
        if tag2 is not None:
            self._values["tag2"] = tag2
        if tag3 is not None:
            self._values["tag3"] = tag3
        if tags is not None:
            self._values["tags"] = tags
        if valid_until is not None:
            self._values["valid_until"] = valid_until
        if vpc_subnet is not None:
            self._values["vpc_subnet"] = vpc_subnet

    @builtins.property
    def gitlabtoken(self) -> builtins.str:
        '''(experimental) Gitlab token for the Register Runner .

        :default: - You must to give the token !!!

        :stability: experimental

        Example::

            new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN' });
        '''
        result = self._values.get("gitlabtoken")
        assert result is not None, "Required property 'gitlabtoken' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def block_duration(self) -> typing.Optional[BlockDuration]:
        '''(experimental) Reservce the Spot Runner instance as spot block with defined duration.

        :default: - BlockDuration.ONE_HOUR , !!! only support spotfleet runner !!! .

        :stability: experimental
        '''
        result = self._values.get("block_duration")
        return typing.cast(typing.Optional[BlockDuration], result)

    @builtins.property
    def docker_volumes(self) -> typing.Optional[typing.List[DockerVolumes]]:
        '''(experimental) add another Gitlab Container Runner Docker Volumes Path at job runner runtime.

        more detail see https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section

        :default: - already mount "/var/run/docker.sock:/var/run/docker.sock"

        :stability: experimental

        Example::

            dockerVolumes: [
              {
                hostPath: '/tmp/cache',
                containerPath: '/tmp/cache',
              },
            ],
        '''
        result = self._values.get("docker_volumes")
        return typing.cast(typing.Optional[typing.List[DockerVolumes]], result)

    @builtins.property
    def ebs_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Gitlab Runner instance EBS size .

        :default: - ebsSize=60

        :stability: experimental

        Example::

            const runner = new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN',ebsSize: 100});
        '''
        result = self._values.get("ebs_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ec2iamrole(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) IAM role for the Gitlab Runner Instance .

        :default: - new Role for Gitlab Runner Instance , attach AmazonSSMManagedInstanceCore Policy .

        :stability: experimental

        Example::

            const role = new Role(stack, 'runner-role', {
              assumedBy: new ServicePrincipal('ec2.amazonaws.com'),
              description: 'For Gitlab EC2 Runner Test Role',
              roleName: 'Myself-Runner-Role',
            });
            
            new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN', ec2iamrole: role });
        '''
        result = self._values.get("ec2iamrole")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def ec2type(self) -> typing.Optional[builtins.str]:
        '''(experimental) Runner default EC2 instance type.

        :default: - t3.micro

        :stability: experimental

        Example::

            new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN', ec2type: 't3.small' });
        '''
        result = self._values.get("ec2type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlab_runner_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Image URL of Gitlab Runner.

        :default: public.ecr.aws/gitlab/gitlab-runner:alpine

        :stability: experimental

        Example::

            new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN', gitlabRunnerImage: 'gitlab/gitlab-runner:alpine' });
        '''
        result = self._values.get("gitlab_runner_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlaburl(self) -> typing.Optional[builtins.str]:
        '''(experimental) Gitlab Runner register url .

        :default: - gitlaburl='https://gitlab.com/' , please use https://yourgitlab.com/ do not use https://yourgitlab.com

        :stability: experimental

        Example::

            const runner = new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN',gitlaburl: 'https://gitlab.com/'});
        '''
        result = self._values.get("gitlaburl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_interruption_behavior(
        self,
    ) -> typing.Optional["InstanceInterruptionBehavior"]:
        '''(experimental) The behavior when a Spot Runner Instance is interrupted.

        :default: - InstanceInterruptionBehavior.TERMINATE , !!! only support spotfleet runner !!! .

        :stability: experimental
        '''
        result = self._values.get("instance_interruption_behavior")
        return typing.cast(typing.Optional["InstanceInterruptionBehavior"], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) SSH key name.

        :default: - no ssh key will be assigned , !!! only support spotfleet runner !!! .

        :stability: experimental
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def selfvpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC for the Gitlab Runner .

        :default: - new VPC will be created , 1 Vpc , 2 Public Subnet .

        :stability: experimental

        Example::

            const newvpc = new Vpc(stack, 'NEWVPC', {
              cidr: '10.1.0.0/16',
              maxAzs: 2,
              subnetConfiguration: [{
                cidrMask: 26,
                name: 'RunnerVPC',
                subnetType: SubnetType.PUBLIC,
              }],
              natGateways: 0,
            });
            
            new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN', selfvpc: newvpc });
        '''
        result = self._values.get("selfvpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def spot_fleet(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Gitlab Runner instance Use Spot Fleet or not ?!.

        :default: - spotFleet=false

        :stability: experimental

        Example::

            const runner = new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN',spotFleet: true});
        '''
        result = self._values.get("spot_fleet")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def tag1(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Gitlab Runner register tag1  .

        :default: - tag1: gitlab .

        :deprecated: - use tags ['runner', 'gitlab', 'awscdk']

        :stability: deprecated

        Example::

            new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN', tag1: 'aa' });
        '''
        result = self._values.get("tag1")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag2(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Gitlab Runner register tag2  .

        :default: - tag2: awscdk .

        :deprecated: - use tags ['runner', 'gitlab', 'awscdk']

        :stability: deprecated

        Example::

            new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN', tag2: 'bb' });
        '''
        result = self._values.get("tag2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag3(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Gitlab Runner register tag3  .

        :default: - tag3: runner .

        :deprecated: - use tags ['runner', 'gitlab', 'awscdk']

        :stability: deprecated

        Example::

            new GitlabContainerRunner(stack, 'runner', { gitlabtoken: 'GITLAB_TOKEN', tag3: 'cc' });
        '''
        result = self._values.get("tag3")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) tags for the runner.

        :default: - ['runner', 'gitlab', 'awscdk']

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def valid_until(self) -> typing.Optional[builtins.str]:
        '''(experimental) the time when the spot fleet allocation expires.

        :default: - no expiration , !!! only support spotfleet runner !!! .

        :stability: experimental
        '''
        result = self._values.get("valid_until")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_subnet(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''(experimental) VPC subnet for the spot fleet.

        :default: - public subnet

        :stability: experimental

        Example::

            const vpc = new Vpc(stack, 'nat', {
            natGateways: 1,
            maxAzs: 2,
            });
            const runner = new GitlabContainerRunner(stack, 'testing', {
              gitlabtoken: 'GITLAB_TOKEN',
              ec2type: 't3.large',
              ec2iamrole: role,
              ebsSize: 100,
              selfvpc: vpc,
              vpcSubnet: {
                subnetType: SubnetType.PUBLIC,
              },
            });
        '''
        result = self._values.get("vpc_subnet")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabContainerRunnerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GitlabRunnerAutoscaling(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-gitlab-runner.GitlabRunnerAutoscaling",
):
    '''(experimental) GitlabRunnerAutoscaling Construct for create Autoscaling Gitlab Runner.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        gitlab_token: builtins.str,
        alarms: typing.Optional[typing.Sequence[typing.Mapping[typing.Any, typing.Any]]] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        docker_volumes: typing.Optional[typing.Sequence[DockerVolumes]] = None,
        ebs_size: typing.Optional[jsii.Number] = None,
        gitlab_runner_image: typing.Optional[builtins.str] = None,
        gitlab_url: typing.Optional[builtins.str] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        instance_type: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        spot_instance: typing.Optional[builtins.bool] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param gitlab_token: (experimental) Gitlab token.
        :param alarms: (experimental) Parameters of put_metric_alarm function. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.put_metric_alarm Default: - [{ AlarmName: 'GitlabRunnerDiskUsage', MetricName: 'disk_used_percent', }]
        :param desired_capacity: (experimental) Desired capacity limit for autoscaling group. Default: - minCapacity, and leave unchanged during deployment
        :param docker_volumes: (experimental) add another Gitlab Container Runner Docker Volumes Path at job runner runtime. more detail see https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section Default: - already mount "/var/run/docker.sock:/var/run/docker.sock"
        :param ebs_size: (experimental) Gitlab Runner instance EBS size . Default: - ebsSize=60
        :param gitlab_runner_image: (experimental) Image URL of Gitlab Runner. Default: public.ecr.aws/gitlab/gitlab-runner:alpine
        :param gitlab_url: (experimental) Gitlab Runner register url . Default: - https://gitlab.com/ , The trailing slash is mandatory.
        :param instance_role: (experimental) IAM role for the Gitlab Runner Instance . Default: - new Role for Gitlab Runner Instance , attach AmazonSSMManagedInstanceCore Policy .
        :param instance_type: (experimental) Runner default EC2 instance type. Default: - t3.micro
        :param max_capacity: (experimental) Maximum capacity limit for autoscaling group. Default: - desiredCapacity
        :param min_capacity: (experimental) Minimum capacity limit for autoscaling group. Default: - minCapacity: 1
        :param spot_instance: (experimental) Run worker nodes as EC2 Spot. Default: - false
        :param tags: (experimental) tags for the runner. Default: - ['runner', 'gitlab', 'awscdk']
        :param vpc: (experimental) VPC for the Gitlab Runner . Default: - A new VPC will be created.
        :param vpc_subnet: (experimental) VPC subnet. Default: - private subnet

        :stability: experimental
        '''
        props = GitlabRunnerAutoscalingProps(
            gitlab_token=gitlab_token,
            alarms=alarms,
            desired_capacity=desired_capacity,
            docker_volumes=docker_volumes,
            ebs_size=ebs_size,
            gitlab_runner_image=gitlab_runner_image,
            gitlab_url=gitlab_url,
            instance_role=instance_role,
            instance_type=instance_type,
            max_capacity=max_capacity,
            min_capacity=min_capacity,
            spot_instance=spot_instance,
            tags=tags,
            vpc=vpc,
            vpc_subnet=vpc_subnet,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createUserData")
    def create_user_data(
        self,
        *,
        gitlab_token: builtins.str,
        alarms: typing.Optional[typing.Sequence[typing.Mapping[typing.Any, typing.Any]]] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        docker_volumes: typing.Optional[typing.Sequence[DockerVolumes]] = None,
        ebs_size: typing.Optional[jsii.Number] = None,
        gitlab_runner_image: typing.Optional[builtins.str] = None,
        gitlab_url: typing.Optional[builtins.str] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        instance_type: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        spot_instance: typing.Optional[builtins.bool] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> typing.List[builtins.str]:
        '''
        :param gitlab_token: (experimental) Gitlab token.
        :param alarms: (experimental) Parameters of put_metric_alarm function. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.put_metric_alarm Default: - [{ AlarmName: 'GitlabRunnerDiskUsage', MetricName: 'disk_used_percent', }]
        :param desired_capacity: (experimental) Desired capacity limit for autoscaling group. Default: - minCapacity, and leave unchanged during deployment
        :param docker_volumes: (experimental) add another Gitlab Container Runner Docker Volumes Path at job runner runtime. more detail see https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section Default: - already mount "/var/run/docker.sock:/var/run/docker.sock"
        :param ebs_size: (experimental) Gitlab Runner instance EBS size . Default: - ebsSize=60
        :param gitlab_runner_image: (experimental) Image URL of Gitlab Runner. Default: public.ecr.aws/gitlab/gitlab-runner:alpine
        :param gitlab_url: (experimental) Gitlab Runner register url . Default: - https://gitlab.com/ , The trailing slash is mandatory.
        :param instance_role: (experimental) IAM role for the Gitlab Runner Instance . Default: - new Role for Gitlab Runner Instance , attach AmazonSSMManagedInstanceCore Policy .
        :param instance_type: (experimental) Runner default EC2 instance type. Default: - t3.micro
        :param max_capacity: (experimental) Maximum capacity limit for autoscaling group. Default: - desiredCapacity
        :param min_capacity: (experimental) Minimum capacity limit for autoscaling group. Default: - minCapacity: 1
        :param spot_instance: (experimental) Run worker nodes as EC2 Spot. Default: - false
        :param tags: (experimental) tags for the runner. Default: - ['runner', 'gitlab', 'awscdk']
        :param vpc: (experimental) VPC for the Gitlab Runner . Default: - A new VPC will be created.
        :param vpc_subnet: (experimental) VPC subnet. Default: - private subnet

        :return: Array.

        :stability: experimental
        '''
        props = GitlabRunnerAutoscalingProps(
            gitlab_token=gitlab_token,
            alarms=alarms,
            desired_capacity=desired_capacity,
            docker_volumes=docker_volumes,
            ebs_size=ebs_size,
            gitlab_runner_image=gitlab_runner_image,
            gitlab_url=gitlab_url,
            instance_role=instance_role,
            instance_type=instance_type,
            max_capacity=max_capacity,
            min_capacity=min_capacity,
            spot_instance=spot_instance,
            tags=tags,
            vpc=vpc,
            vpc_subnet=vpc_subnet,
        )

        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "createUserData", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoscalingGroup")
    def autoscaling_group(self) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        '''(experimental) This represents a Runner Auto Scaling Group.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_autoscaling.AutoScalingGroup, jsii.get(self, "autoscalingGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> aws_cdk.aws_iam.IRole:
        '''(experimental) The IAM role assumed by the Runner instance.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "instanceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        '''(experimental) The EC2 runner's default SecurityGroup.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, jsii.get(self, "securityGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicAlarm")
    def topic_alarm(self) -> aws_cdk.aws_sns.ITopic:
        '''(experimental) The SNS topic to suscribe alarms for EC2 runner's metrics.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_sns.ITopic, jsii.get(self, "topicAlarm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The EC2 runner's VPC.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-gitlab-runner.GitlabRunnerAutoscalingProps",
    jsii_struct_bases=[],
    name_mapping={
        "gitlab_token": "gitlabToken",
        "alarms": "alarms",
        "desired_capacity": "desiredCapacity",
        "docker_volumes": "dockerVolumes",
        "ebs_size": "ebsSize",
        "gitlab_runner_image": "gitlabRunnerImage",
        "gitlab_url": "gitlabUrl",
        "instance_role": "instanceRole",
        "instance_type": "instanceType",
        "max_capacity": "maxCapacity",
        "min_capacity": "minCapacity",
        "spot_instance": "spotInstance",
        "tags": "tags",
        "vpc": "vpc",
        "vpc_subnet": "vpcSubnet",
    },
)
class GitlabRunnerAutoscalingProps:
    def __init__(
        self,
        *,
        gitlab_token: builtins.str,
        alarms: typing.Optional[typing.Sequence[typing.Mapping[typing.Any, typing.Any]]] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        docker_volumes: typing.Optional[typing.Sequence[DockerVolumes]] = None,
        ebs_size: typing.Optional[jsii.Number] = None,
        gitlab_runner_image: typing.Optional[builtins.str] = None,
        gitlab_url: typing.Optional[builtins.str] = None,
        instance_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        instance_type: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        spot_instance: typing.Optional[builtins.bool] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnet: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''(experimental) GitlabRunnerAutoscaling Props.

        :param gitlab_token: (experimental) Gitlab token.
        :param alarms: (experimental) Parameters of put_metric_alarm function. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.put_metric_alarm Default: - [{ AlarmName: 'GitlabRunnerDiskUsage', MetricName: 'disk_used_percent', }]
        :param desired_capacity: (experimental) Desired capacity limit for autoscaling group. Default: - minCapacity, and leave unchanged during deployment
        :param docker_volumes: (experimental) add another Gitlab Container Runner Docker Volumes Path at job runner runtime. more detail see https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section Default: - already mount "/var/run/docker.sock:/var/run/docker.sock"
        :param ebs_size: (experimental) Gitlab Runner instance EBS size . Default: - ebsSize=60
        :param gitlab_runner_image: (experimental) Image URL of Gitlab Runner. Default: public.ecr.aws/gitlab/gitlab-runner:alpine
        :param gitlab_url: (experimental) Gitlab Runner register url . Default: - https://gitlab.com/ , The trailing slash is mandatory.
        :param instance_role: (experimental) IAM role for the Gitlab Runner Instance . Default: - new Role for Gitlab Runner Instance , attach AmazonSSMManagedInstanceCore Policy .
        :param instance_type: (experimental) Runner default EC2 instance type. Default: - t3.micro
        :param max_capacity: (experimental) Maximum capacity limit for autoscaling group. Default: - desiredCapacity
        :param min_capacity: (experimental) Minimum capacity limit for autoscaling group. Default: - minCapacity: 1
        :param spot_instance: (experimental) Run worker nodes as EC2 Spot. Default: - false
        :param tags: (experimental) tags for the runner. Default: - ['runner', 'gitlab', 'awscdk']
        :param vpc: (experimental) VPC for the Gitlab Runner . Default: - A new VPC will be created.
        :param vpc_subnet: (experimental) VPC subnet. Default: - private subnet

        :stability: experimental
        '''
        if isinstance(vpc_subnet, dict):
            vpc_subnet = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnet)
        self._values: typing.Dict[str, typing.Any] = {
            "gitlab_token": gitlab_token,
        }
        if alarms is not None:
            self._values["alarms"] = alarms
        if desired_capacity is not None:
            self._values["desired_capacity"] = desired_capacity
        if docker_volumes is not None:
            self._values["docker_volumes"] = docker_volumes
        if ebs_size is not None:
            self._values["ebs_size"] = ebs_size
        if gitlab_runner_image is not None:
            self._values["gitlab_runner_image"] = gitlab_runner_image
        if gitlab_url is not None:
            self._values["gitlab_url"] = gitlab_url
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if min_capacity is not None:
            self._values["min_capacity"] = min_capacity
        if spot_instance is not None:
            self._values["spot_instance"] = spot_instance
        if tags is not None:
            self._values["tags"] = tags
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnet is not None:
            self._values["vpc_subnet"] = vpc_subnet

    @builtins.property
    def gitlab_token(self) -> builtins.str:
        '''(experimental) Gitlab token.

        :stability: experimental

        Example::

            new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN' });
        '''
        result = self._values.get("gitlab_token")
        assert result is not None, "Required property 'gitlab_token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alarms(
        self,
    ) -> typing.Optional[typing.List[typing.Mapping[typing.Any, typing.Any]]]:
        '''(experimental) Parameters of put_metric_alarm function.

        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.put_metric_alarm

        :default:

        - [{
        AlarmName: 'GitlabRunnerDiskUsage',
        MetricName: 'disk_used_percent',
        }]

        :stability: experimental
        '''
        result = self._values.get("alarms")
        return typing.cast(typing.Optional[typing.List[typing.Mapping[typing.Any, typing.Any]]], result)

    @builtins.property
    def desired_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Desired capacity limit for autoscaling group.

        :default: - minCapacity, and leave unchanged during deployment

        :stability: experimental

        Example::

            new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN', desiredCapacity: 2 });
        '''
        result = self._values.get("desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def docker_volumes(self) -> typing.Optional[typing.List[DockerVolumes]]:
        '''(experimental) add another Gitlab Container Runner Docker Volumes Path at job runner runtime.

        more detail see https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section

        :default: - already mount "/var/run/docker.sock:/var/run/docker.sock"

        :stability: experimental

        Example::

            dockerVolumes: [
              {
                hostPath: '/tmp/cache',
                containerPath: '/tmp/cache',
              },
            ],
        '''
        result = self._values.get("docker_volumes")
        return typing.cast(typing.Optional[typing.List[DockerVolumes]], result)

    @builtins.property
    def ebs_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Gitlab Runner instance EBS size .

        :default: - ebsSize=60

        :stability: experimental

        Example::

            const runner = new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN', ebsSize: 100});
        '''
        result = self._values.get("ebs_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def gitlab_runner_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Image URL of Gitlab Runner.

        :default: public.ecr.aws/gitlab/gitlab-runner:alpine

        :stability: experimental

        Example::

            new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN', gitlabRunnerImage: 'gitlab/gitlab-runner:alpine' });
        '''
        result = self._values.get("gitlab_runner_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlab_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Gitlab Runner register url .

        :default: - https://gitlab.com/ , The trailing slash is mandatory.

        :stability: experimental

        Example::

            const runner = new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN',gitlabUrl: 'https://gitlab.com/'});
        '''
        result = self._values.get("gitlab_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) IAM role for the Gitlab Runner Instance .

        :default: - new Role for Gitlab Runner Instance , attach AmazonSSMManagedInstanceCore Policy .

        :stability: experimental

        Example::

            const role = new Role(stack, 'runner-role', {
              assumedBy: new ServicePrincipal('ec2.amazonaws.com'),
              description: 'For Gitlab Runner Test Role',
              roleName: 'Runner-Role',
            });
            
            new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN', instanceRole: role });
        '''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) Runner default EC2 instance type.

        :default: - t3.micro

        :stability: experimental

        Example::

            new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN', instanceType: 't3.small' });
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Maximum capacity limit for autoscaling group.

        :default: - desiredCapacity

        :stability: experimental

        Example::

            new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN', maxCapacity: 4 });
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimum capacity limit for autoscaling group.

        :default: - minCapacity: 1

        :stability: experimental

        Example::

            new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN', minCapacity: 2 });
        '''
        result = self._values.get("min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def spot_instance(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Run worker nodes as EC2 Spot.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("spot_instance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) tags for the runner.

        :default: - ['runner', 'gitlab', 'awscdk']

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC for the Gitlab Runner .

        :default: - A new VPC will be created.

        :stability: experimental

        Example::

            const newVpc = new Vpc(stack, 'NewVPC', {
              cidr: '10.1.0.0/16',
              maxAzs: 2,
              subnetConfiguration: [{
                cidrMask: 26,
                name: 'RunnerVPC',
                subnetType: SubnetType.PUBLIC,
              }],
              natGateways: 0,
            });
            
            new GitlabRunnerAutoscaling(stack, 'runner', { gitlabToken: 'GITLAB_TOKEN', vpc: newVpc });
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnet(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''(experimental) VPC subnet.

        :default: - private subnet

        :stability: experimental

        Example::

            const vpc = new Vpc(stack, 'nat', {
            natGateways: 1,
            maxAzs: 2,
            });
            const runner = new GitlabRunnerAutoscaling(stack, 'testing', {
              gitlabToken: 'GITLAB_TOKEN',
              instanceType: 't3.large',
              instanceRole: role,
              ebsSize: 100,
              vpc: vpc,
              vpcSubnet: {
                subnetType: SubnetType.PUBLIC,
              },
            });
        '''
        result = self._values.get("vpc_subnet")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitlabRunnerAutoscalingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-gitlab-runner.InstanceInterruptionBehavior")
class InstanceInterruptionBehavior(enum.Enum):
    '''(experimental) InstanceInterruptionBehavior enum.

    :stability: experimental
    '''

    HIBERNATE = "HIBERNATE"
    '''(experimental) hibernate.

    :stability: experimental
    '''
    STOP = "STOP"
    '''(experimental) stop.

    :stability: experimental
    '''
    TERMINATE = "TERMINATE"
    '''(experimental) terminate.

    :stability: experimental
    '''


__all__ = [
    "BlockDuration",
    "DockerVolumes",
    "GitlabContainerRunner",
    "GitlabContainerRunnerProps",
    "GitlabRunnerAutoscaling",
    "GitlabRunnerAutoscalingProps",
    "InstanceInterruptionBehavior",
]

publication.publish()
