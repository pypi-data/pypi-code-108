'''
# AWS Batch Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

AWS Batch is a batch processing tool for efficiently running hundreds of thousands computing jobs in AWS. Batch can dynamically provision different types of compute resources based on the resource requirements of submitted jobs.

AWS Batch simplifies the planning, scheduling, and executions of your batch workloads across a full range of compute services like [Amazon EC2](https://aws.amazon.com/ec2/) and [Spot Resources](https://aws.amazon.com/ec2/spot/).

Batch achieves this by utilizing queue processing of batch job requests. To successfully submit a job for execution, you need the following resources:

1. [Job Definition](#job-definition) - *Group various job properties (container image, resource requirements, env variables...) into a single definition. These definitions are used at job submission time.*
2. [Compute Environment](#compute-environment) - *the execution runtime of submitted batch jobs*
3. [Job Queue](#job-queue) - *the queue where batch jobs can be submitted to via AWS SDK/CLI*

For more information on **AWS Batch** visit the [AWS Docs for Batch](https://docs.aws.amazon.com/batch/index.html).

## Compute Environment

At the core of AWS Batch is the compute environment. All batch jobs are processed within a compute environment, which uses resource like OnDemand/Spot EC2 instances or Fargate.

In **MANAGED** mode, AWS will handle the provisioning of compute resources to accommodate the demand. Otherwise, in **UNMANAGED** mode, you will need to manage the provisioning of those resources.

Below is an example of each available type of compute environment:

```python
# vpc: ec2.Vpc


# default is managed
aws_managed_environment = batch.ComputeEnvironment(self, "AWS-Managed-Compute-Env",
    compute_resources=batch.ComputeResources(
        vpc=vpc
    )
)

customer_managed_environment = batch.ComputeEnvironment(self, "Customer-Managed-Compute-Env",
    managed=False
)
```

### Spot-Based Compute Environment

It is possible to have AWS Batch submit spotfleet requests for obtaining compute resources. Below is an example of how this can be done:

```python
vpc = ec2.Vpc(self, "VPC")

spot_environment = batch.ComputeEnvironment(self, "MySpotEnvironment",
    compute_resources=batch.ComputeResources(
        type=batch.ComputeResourceType.SPOT,
        bid_percentage=75,  # Bids for resources at 75% of the on-demand price
        vpc=vpc
    )
)
```

### Fargate Compute Environment

It is possible to have AWS Batch submit jobs to be run on Fargate compute resources. Below is an example of how this can be done:

```python
vpc = ec2.Vpc(self, "VPC")

fargate_spot_environment = batch.ComputeEnvironment(self, "MyFargateEnvironment",
    compute_resources=batch.ComputeResources(
        type=batch.ComputeResourceType.FARGATE_SPOT,
        vpc=vpc
    )
)
```

### Understanding Progressive Allocation Strategies

AWS Batch uses an [allocation strategy](https://docs.aws.amazon.com/batch/latest/userguide/allocation-strategies.html) to determine what compute resource will efficiently handle incoming job requests. By default, **BEST_FIT** will pick an available compute instance based on vCPU requirements. If none exist, the job will wait until resources become available. However, with this strategy, you may have jobs waiting in the queue unnecessarily despite having more powerful instances available. Below is an example of how that situation might look like:

```plaintext
Compute Environment:

1. m5.xlarge => 4 vCPU
2. m5.2xlarge => 8 vCPU
```

```plaintext
Job Queue:
---------
| A | B |
---------

Job Requirements:
A => 4 vCPU - ALLOCATED TO m5.xlarge
B => 2 vCPU - WAITING
```

In this situation, Batch will allocate **Job A** to compute resource #1 because it is the most cost efficient resource that matches the vCPU requirement. However, with this `BEST_FIT` strategy, **Job B** will not be allocated to our other available compute resource even though it is strong enough to handle it. Instead, it will wait until the first job is finished processing or wait a similar `m5.xlarge` resource to be provisioned.

The alternative would be to use the `BEST_FIT_PROGRESSIVE` strategy in order for the remaining job to be handled in larger containers regardless of vCPU requirement and costs.

### Launch template support

Simply define your Launch Template:

```text
// This example is only available in TypeScript
const myLaunchTemplate = new ec2.CfnLaunchTemplate(this, 'LaunchTemplate', {
  launchTemplateName: 'extra-storage-template',
  launchTemplateData: {
    blockDeviceMappings: [
      {
        deviceName: '/dev/xvdcz',
        ebs: {
          encrypted: true,
          volumeSize: 100,
          volumeType: 'gp2',
        },
      },
    ],
  },
});
```

and use it:

```python
# vpc: ec2.Vpc
# my_launch_template: ec2.CfnLaunchTemplate


my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
    compute_resources=batch.ComputeResources(
        launch_template=batch.LaunchTemplateSpecification(
            launch_template_name=my_launch_template.launch_template_name
        ),
        vpc=vpc
    ),
    compute_environment_name="MyStorageCapableComputeEnvironment"
)
```

### Importing an existing Compute Environment

To import an existing batch compute environment, call `ComputeEnvironment.fromComputeEnvironmentArn()`.

Below is an example:

```python
compute_env = batch.ComputeEnvironment.from_compute_environment_arn(self, "imported-compute-env", "arn:aws:batch:us-east-1:555555555555:compute-environment/My-Compute-Env")
```

### Change the baseline AMI of the compute resources

Occasionally, you will need to deviate from the default processing AMI.

ECS Optimized Amazon Linux 2 example:

```python
# vpc: ec2.Vpc

my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
    compute_resources=batch.ComputeResources(
        image=ecs.EcsOptimizedAmi(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        ),
        vpc=vpc
    )
)
```

Custom based AMI example:

```python
# vpc: ec2.Vpc

my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
    compute_resources=batch.ComputeResources(
        image=ec2.MachineImage.generic_linux({
            "[aws-region]": "[ami-ID]"
        }),
        vpc=vpc
    )
)
```

## Job Queue

Jobs are always submitted to a specific queue. This means that you have to create a queue before you can start submitting jobs. Each queue is mapped to at least one (and no more than three) compute environment. When the job is scheduled for execution, AWS Batch will select the compute environment based on ordinal priority and available capacity in each environment.

```python
# compute_environment: batch.ComputeEnvironment

job_queue = batch.JobQueue(self, "JobQueue",
    compute_environments=[batch.JobQueueComputeEnvironment(
        # Defines a collection of compute resources to handle assigned batch jobs
        compute_environment=compute_environment,
        # Order determines the allocation order for jobs (i.e. Lower means higher preference for job assignment)
        order=1
    )
    ]
)
```

### Priorty-Based Queue Example

Sometimes you might have jobs that are more important than others, and when submitted, should take precedence over the existing jobs. To achieve this, you can create a priority based execution strategy, by assigning each queue its own priority:

```python
# shared_compute_envs: batch.ComputeEnvironment

high_prio_queue = batch.JobQueue(self, "JobQueue",
    compute_environments=[batch.JobQueueComputeEnvironment(
        compute_environment=shared_compute_envs,
        order=1
    )],
    priority=2
)

low_prio_queue = batch.JobQueue(self, "JobQueue",
    compute_environments=[batch.JobQueueComputeEnvironment(
        compute_environment=shared_compute_envs,
        order=1
    )],
    priority=1
)
```

By making sure to use the same compute environments between both job queues, we will give precedence to the `highPrioQueue` for the assigning of jobs to available compute environments.

### Importing an existing Job Queue

To import an existing batch job queue, call `JobQueue.fromJobQueueArn()`.

Below is an example:

```python
job_queue = batch.JobQueue.from_job_queue_arn(self, "imported-job-queue", "arn:aws:batch:us-east-1:555555555555:job-queue/High-Prio-Queue")
```

## Job Definition

A Batch Job definition helps AWS Batch understand important details about how to run your application in the scope of a Batch Job. This involves key information like resource requirements, what containers to run, how the compute environment should be prepared, and more. Below is a simple example of how to create a job definition:

```python
import aws_cdk.aws_ecr as ecr


repo = ecr.Repository.from_repository_name(self, "batch-job-repo", "todo-list")

batch.JobDefinition(self, "batch-job-def-from-ecr",
    container=batch.JobDefinitionContainer(
        image=ecs.EcrImage(repo, "latest")
    )
)
```

### Using a local Docker project

Below is an example of how you can create a Batch Job Definition from a local Docker application.

```python
batch.JobDefinition(self, "batch-job-def-from-local",
    container=batch.JobDefinitionContainer(
        # todo-list is a directory containing a Dockerfile to build the application
        image=ecs.ContainerImage.from_asset("../todo-list")
    )
)
```

### Providing custom log configuration

You can provide custom log driver and its configuration for the container.

```python
import aws_cdk.aws_ssm as ssm


batch.JobDefinition(self, "job-def",
    container=batch.JobDefinitionContainer(
        image=ecs.EcrImage.from_registry("docker/whalesay"),
        log_configuration=batch.LogConfiguration(
            log_driver=batch.LogDriver.AWSLOGS,
            options={"awslogs-region": "us-east-1"},
            secret_options=[
                batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
            ]
        )
    )
)
```

### Importing an existing Job Definition

#### From ARN

To import an existing batch job definition from its ARN, call `JobDefinition.fromJobDefinitionArn()`.

Below is an example:

```python
job = batch.JobDefinition.from_job_definition_arn(self, "imported-job-definition", "arn:aws:batch:us-east-1:555555555555:job-definition/my-job-definition")
```

#### From Name

To import an existing batch job definition from its name, call `JobDefinition.fromJobDefinitionName()`.
If name is specified without a revision then the latest active revision is used.

Below is an example:

```python
# Without revision
job1 = batch.JobDefinition.from_job_definition_name(self, "imported-job-definition", "my-job-definition")

# With revision
job2 = batch.JobDefinition.from_job_definition_name(self, "imported-job-definition", "my-job-definition:3")
```
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
import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_iam
import aws_cdk.aws_secretsmanager
import aws_cdk.aws_ssm
import constructs


@jsii.enum(jsii_type="@aws-cdk/aws-batch-alpha.AllocationStrategy")
class AllocationStrategy(enum.Enum):
    '''(experimental) Properties for how to prepare compute resources that are provisioned for a compute environment.

    :stability: experimental
    '''

    BEST_FIT = "BEST_FIT"
    '''(experimental) Batch will use the best fitting instance type will be used when assigning a batch job in this compute environment.

    :stability: experimental
    '''
    BEST_FIT_PROGRESSIVE = "BEST_FIT_PROGRESSIVE"
    '''(experimental) Batch will select additional instance types that are large enough to meet the requirements of the jobs in the queue, with a preference for instance types with a lower cost per unit vCPU.

    :stability: experimental
    '''
    SPOT_CAPACITY_OPTIMIZED = "SPOT_CAPACITY_OPTIMIZED"
    '''(experimental) This is only available for Spot Instance compute resources and will select additional instance types that are large enough to meet the requirements of the jobs in the queue, with a preference for instance types that are less likely to be interrupted.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch-alpha.ComputeEnvironmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "compute_environment_name": "computeEnvironmentName",
        "compute_resources": "computeResources",
        "enabled": "enabled",
        "managed": "managed",
        "service_role": "serviceRole",
    },
)
class ComputeEnvironmentProps:
    def __init__(
        self,
        *,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional["ComputeResources"] = None,
        enabled: typing.Optional[builtins.bool] = None,
        managed: typing.Optional[builtins.bool] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''(experimental) Properties for creating a new Compute Environment.

        :param compute_environment_name: (experimental) A name for the compute environment. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: - CloudFormation-generated name
        :param compute_resources: (experimental) The details of the required compute resources for the managed compute environment. If specified, and this is an unmanaged compute environment, will throw an error. By default, AWS Batch managed compute environments use a recent, approved version of the Amazon ECS-optimized AMI for compute resources. Default: - CloudFormation defaults
        :param enabled: (experimental) The state of the compute environment. If the state is set to true, then the compute environment accepts jobs from a queue and can scale out automatically based on queues. Default: true
        :param managed: (experimental) Determines if AWS should manage the allocation of compute resources for processing jobs. If set to false, then you are in charge of providing the compute resource details. Default: true
        :param service_role: (experimental) The IAM role used by Batch to make calls to other AWS services on your behalf for managing the resources that you use with the service. By default, this role is created for you using the AWS managed service policy for Batch. Default: - Role using the 'service-role/AWSBatchServiceRole' policy.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            
            my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
                compute_resources=batch.ComputeResources(
                    image=ecs.EcsOptimizedAmi(
                        generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
                    ),
                    vpc=vpc
                )
            )
        '''
        if isinstance(compute_resources, dict):
            compute_resources = ComputeResources(**compute_resources)
        self._values: typing.Dict[str, typing.Any] = {}
        if compute_environment_name is not None:
            self._values["compute_environment_name"] = compute_environment_name
        if compute_resources is not None:
            self._values["compute_resources"] = compute_resources
        if enabled is not None:
            self._values["enabled"] = enabled
        if managed is not None:
            self._values["managed"] = managed
        if service_role is not None:
            self._values["service_role"] = service_role

    @builtins.property
    def compute_environment_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the compute environment.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :default: - CloudFormation-generated name

        :stability: experimental
        '''
        result = self._values.get("compute_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compute_resources(self) -> typing.Optional["ComputeResources"]:
        '''(experimental) The details of the required compute resources for the managed compute environment.

        If specified, and this is an unmanaged compute environment, will throw an error.

        By default, AWS Batch managed compute environments use a recent, approved version of the
        Amazon ECS-optimized AMI for compute resources.

        :default: - CloudFormation defaults

        :stability: experimental
        :link: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-batch-computeenvironment-computeresources.html
        '''
        result = self._values.get("compute_resources")
        return typing.cast(typing.Optional["ComputeResources"], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The state of the compute environment.

        If the state is set to true, then the compute
        environment accepts jobs from a queue and can scale out automatically based on queues.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def managed(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Determines if AWS should manage the allocation of compute resources for processing jobs.

        If set to false, then you are in charge of providing the compute resource details.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("managed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def service_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM role used by Batch to make calls to other AWS services on your behalf for managing the resources that you use with the service.

        By default, this role is created for you using
        the AWS managed service policy for Batch.

        :default: - Role using the 'service-role/AWSBatchServiceRole' policy.

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/service_IAM_role.html
        '''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeEnvironmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-batch-alpha.ComputeResourceType")
class ComputeResourceType(enum.Enum):
    '''(experimental) Property to specify if the compute environment uses On-Demand, SpotFleet, Fargate, or Fargate Spot compute resources.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        vpc = ec2.Vpc(self, "VPC")
        
        spot_environment = batch.ComputeEnvironment(self, "MySpotEnvironment",
            compute_resources=batch.ComputeResources(
                type=batch.ComputeResourceType.SPOT,
                bid_percentage=75,  # Bids for resources at 75% of the on-demand price
                vpc=vpc
            )
        )
    '''

    ON_DEMAND = "ON_DEMAND"
    '''(experimental) Resources will be EC2 On-Demand resources.

    :stability: experimental
    '''
    SPOT = "SPOT"
    '''(experimental) Resources will be EC2 SpotFleet resources.

    :stability: experimental
    '''
    FARGATE = "FARGATE"
    '''(experimental) Resources will be Fargate resources.

    :stability: experimental
    '''
    FARGATE_SPOT = "FARGATE_SPOT"
    '''(experimental) Resources will be Fargate Spot resources.

    Fargate Spot uses spare capacity in the AWS cloud to run your fault-tolerant,
    time-flexible jobs at up to a 70% discount. If AWS needs the resources back,
    jobs running on Fargate Spot will be interrupted with two minutes of notification.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch-alpha.ComputeResources",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "allocation_strategy": "allocationStrategy",
        "bid_percentage": "bidPercentage",
        "compute_resources_tags": "computeResourcesTags",
        "desiredv_cpus": "desiredvCpus",
        "ec2_key_pair": "ec2KeyPair",
        "image": "image",
        "instance_role": "instanceRole",
        "instance_types": "instanceTypes",
        "launch_template": "launchTemplate",
        "maxv_cpus": "maxvCpus",
        "minv_cpus": "minvCpus",
        "placement_group": "placementGroup",
        "security_groups": "securityGroups",
        "spot_fleet_role": "spotFleetRole",
        "type": "type",
        "vpc_subnets": "vpcSubnets",
    },
)
class ComputeResources:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        allocation_strategy: typing.Optional[AllocationStrategy] = None,
        bid_percentage: typing.Optional[jsii.Number] = None,
        compute_resources_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        desiredv_cpus: typing.Optional[jsii.Number] = None,
        ec2_key_pair: typing.Optional[builtins.str] = None,
        image: typing.Optional[aws_cdk.aws_ec2.IMachineImage] = None,
        instance_role: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.InstanceType]] = None,
        launch_template: typing.Optional["LaunchTemplateSpecification"] = None,
        maxv_cpus: typing.Optional[jsii.Number] = None,
        minv_cpus: typing.Optional[jsii.Number] = None,
        placement_group: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        spot_fleet_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        type: typing.Optional[ComputeResourceType] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''(experimental) Properties for defining the structure of the batch compute cluster.

        :param vpc: (experimental) The VPC network that all compute resources will be connected to.
        :param allocation_strategy: (experimental) The allocation strategy to use for the compute resource in case not enough instances of the best fitting instance type can be allocated. This could be due to availability of the instance type in the region or Amazon EC2 service limits. If this is not specified, the default for the EC2 ComputeResourceType is BEST_FIT, which will use only the best fitting instance type, waiting for additional capacity if it's not available. This allocation strategy keeps costs lower but can limit scaling. If you are using Spot Fleets with BEST_FIT then the Spot Fleet IAM Role must be specified. BEST_FIT_PROGRESSIVE will select an additional instance type that is large enough to meet the requirements of the jobs in the queue, with a preference for an instance type with a lower cost. The default value for the SPOT instance type is SPOT_CAPACITY_OPTIMIZED, which is only available for for this type of compute resources and will select an additional instance type that is large enough to meet the requirements of the jobs in the queue, with a preference for an instance type that is less likely to be interrupted. Default: AllocationStrategy.BEST_FIT
        :param bid_percentage: (experimental) This property will be ignored if you set the environment type to ON_DEMAND. The maximum percentage that a Spot Instance price can be when compared with the On-Demand price for that instance type before instances are launched. For example, if your maximum percentage is 20%, then the Spot price must be below 20% of the current On-Demand price for that EC2 instance. You always pay the lowest (market) price and never more than your maximum percentage. If you leave this field empty, the default value is 100% of the On-Demand price. Default: 100
        :param compute_resources_tags: (experimental) Key-value pair tags to be applied to resources that are launched in the compute environment. For AWS Batch, these take the form of "String1": "String2", where String1 is the tag key and String2 is the tag value—for example, { "Name": "AWS Batch Instance - C4OnDemand" }. Default: - no tags will be assigned on compute resources.
        :param desiredv_cpus: (experimental) The desired number of EC2 vCPUS in the compute environment. Default: - no desired vcpu value will be used.
        :param ec2_key_pair: (experimental) The EC2 key pair that is used for instances launched in the compute environment. If no key is defined, then SSH access is not allowed to provisioned compute resources. Default: - no SSH access will be possible.
        :param image: (experimental) The Amazon Machine Image (AMI) ID used for instances launched in the compute environment. Default: - no image will be used.
        :param instance_role: (experimental) The Amazon ECS instance profile applied to Amazon EC2 instances in a compute environment. You can specify the short name or full Amazon Resource Name (ARN) of an instance profile. For example, ecsInstanceRole or arn:aws:iam::<aws_account_id>:instance-profile/ecsInstanceRole . For more information, see Amazon ECS Instance Role in the AWS Batch User Guide. Default: - a new role will be created.
        :param instance_types: (experimental) The types of EC2 instances that may be launched in the compute environment. You can specify instance families to launch any instance type within those families (for example, c4 or p3), or you can specify specific sizes within a family (such as c4.8xlarge). You can also choose optimal to pick instance types (from the C, M, and R instance families) on the fly that match the demand of your job queues. Default: optimal
        :param launch_template: (experimental) An optional launch template to associate with your compute resources. For more information, see README file. Default: - no custom launch template will be used
        :param maxv_cpus: (experimental) The maximum number of EC2 vCPUs that an environment can reach. Each vCPU is equivalent to 1,024 CPU shares. You must specify at least one vCPU. Default: 256
        :param minv_cpus: (experimental) The minimum number of EC2 vCPUs that an environment should maintain (even if the compute environment state is DISABLED). Each vCPU is equivalent to 1,024 CPU shares. By keeping this set to 0 you will not have instance time wasted when there is no work to be run. If you set this above zero you will maintain that number of vCPUs at all times. Default: 0
        :param placement_group: (experimental) The Amazon EC2 placement group to associate with your compute resources. Default: - No placement group will be used.
        :param security_groups: (experimental) The EC2 security group(s) associated with instances launched in the compute environment. Default: - AWS default security group.
        :param spot_fleet_role: (experimental) This property will be ignored if you set the environment type to ON_DEMAND. The Amazon Resource Name (ARN) of the Amazon EC2 Spot Fleet IAM role applied to a SPOT compute environment. For more information, see Amazon EC2 Spot Fleet Role in the AWS Batch User Guide. Default: - no fleet role will be used.
        :param type: (experimental) The type of compute environment: ON_DEMAND, SPOT, FARGATE, or FARGATE_SPOT. Default: ON_DEMAND
        :param vpc_subnets: (experimental) The VPC subnets into which the compute resources are launched. Default: - private subnets of the supplied VPC.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            
            my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
                compute_resources=batch.ComputeResources(
                    image=ecs.EcsOptimizedAmi(
                        generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
                    ),
                    vpc=vpc
                )
            )
        '''
        if isinstance(launch_template, dict):
            launch_template = LaunchTemplateSpecification(**launch_template)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if allocation_strategy is not None:
            self._values["allocation_strategy"] = allocation_strategy
        if bid_percentage is not None:
            self._values["bid_percentage"] = bid_percentage
        if compute_resources_tags is not None:
            self._values["compute_resources_tags"] = compute_resources_tags
        if desiredv_cpus is not None:
            self._values["desiredv_cpus"] = desiredv_cpus
        if ec2_key_pair is not None:
            self._values["ec2_key_pair"] = ec2_key_pair
        if image is not None:
            self._values["image"] = image
        if instance_role is not None:
            self._values["instance_role"] = instance_role
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if launch_template is not None:
            self._values["launch_template"] = launch_template
        if maxv_cpus is not None:
            self._values["maxv_cpus"] = maxv_cpus
        if minv_cpus is not None:
            self._values["minv_cpus"] = minv_cpus
        if placement_group is not None:
            self._values["placement_group"] = placement_group
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if spot_fleet_role is not None:
            self._values["spot_fleet_role"] = spot_fleet_role
        if type is not None:
            self._values["type"] = type
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The VPC network that all compute resources will be connected to.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def allocation_strategy(self) -> typing.Optional[AllocationStrategy]:
        '''(experimental) The allocation strategy to use for the compute resource in case not enough instances of the best fitting instance type can be allocated.

        This could be due to availability of the instance type in
        the region or Amazon EC2 service limits. If this is not specified, the default for the EC2
        ComputeResourceType is BEST_FIT, which will use only the best fitting instance type, waiting for
        additional capacity if it's not available. This allocation strategy keeps costs lower but can limit
        scaling. If you are using Spot Fleets with BEST_FIT then the Spot Fleet IAM Role must be specified.
        BEST_FIT_PROGRESSIVE will select an additional instance type that is large enough to meet the
        requirements of the jobs in the queue, with a preference for an instance type with a lower cost.
        The default value for the SPOT instance type is SPOT_CAPACITY_OPTIMIZED, which is only available for
        for this type of compute resources and will select an additional instance type that is large enough
        to meet the requirements of the jobs in the queue, with a preference for an instance type that is
        less likely to be interrupted.

        :default: AllocationStrategy.BEST_FIT

        :stability: experimental
        '''
        result = self._values.get("allocation_strategy")
        return typing.cast(typing.Optional[AllocationStrategy], result)

    @builtins.property
    def bid_percentage(self) -> typing.Optional[jsii.Number]:
        '''(experimental) This property will be ignored if you set the environment type to ON_DEMAND.

        The maximum percentage that a Spot Instance price can be when compared with the On-Demand price for
        that instance type before instances are launched. For example, if your maximum percentage is 20%,
        then the Spot price must be below 20% of the current On-Demand price for that EC2 instance. You always
        pay the lowest (market) price and never more than your maximum percentage. If you leave this field empty,
        the default value is 100% of the On-Demand price.

        :default: 100

        :stability: experimental
        '''
        result = self._values.get("bid_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def compute_resources_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Key-value pair tags to be applied to resources that are launched in the compute environment.

        For AWS Batch, these take the form of "String1": "String2", where String1 is the tag key and
        String2 is the tag value—for example, { "Name": "AWS Batch Instance - C4OnDemand" }.

        :default: - no tags will be assigned on compute resources.

        :stability: experimental
        '''
        result = self._values.get("compute_resources_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def desiredv_cpus(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The desired number of EC2 vCPUS in the compute environment.

        :default: - no desired vcpu value will be used.

        :stability: experimental
        '''
        result = self._values.get("desiredv_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ec2_key_pair(self) -> typing.Optional[builtins.str]:
        '''(experimental) The EC2 key pair that is used for instances launched in the compute environment.

        If no key is defined, then SSH access is not allowed to provisioned compute resources.

        :default: - no SSH access will be possible.

        :stability: experimental
        '''
        result = self._values.get("ec2_key_pair")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image(self) -> typing.Optional[aws_cdk.aws_ec2.IMachineImage]:
        '''(experimental) The Amazon Machine Image (AMI) ID used for instances launched in the compute environment.

        :default: - no image will be used.

        :stability: experimental
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IMachineImage], result)

    @builtins.property
    def instance_role(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Amazon ECS instance profile applied to Amazon EC2 instances in a compute environment.

        You can specify
        the short name or full Amazon Resource Name (ARN) of an instance profile. For example, ecsInstanceRole or
        arn:aws:iam::<aws_account_id>:instance-profile/ecsInstanceRole . For more information, see Amazon ECS
        Instance Role in the AWS Batch User Guide.

        :default: - a new role will be created.

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/instance_IAM_role.html
        '''
        result = self._values.get("instance_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_types(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.InstanceType]]:
        '''(experimental) The types of EC2 instances that may be launched in the compute environment.

        You can specify instance
        families to launch any instance type within those families (for example, c4 or p3), or you can specify
        specific sizes within a family (such as c4.8xlarge). You can also choose optimal to pick instance types
        (from the C, M, and R instance families) on the fly that match the demand of your job queues.

        :default: optimal

        :stability: experimental
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.InstanceType]], result)

    @builtins.property
    def launch_template(self) -> typing.Optional["LaunchTemplateSpecification"]:
        '''(experimental) An optional launch template to associate with your compute resources.

        For more information, see README file.

        :default: - no custom launch template will be used

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/launch-templates.html
        '''
        result = self._values.get("launch_template")
        return typing.cast(typing.Optional["LaunchTemplateSpecification"], result)

    @builtins.property
    def maxv_cpus(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of EC2 vCPUs that an environment can reach.

        Each vCPU is equivalent to
        1,024 CPU shares. You must specify at least one vCPU.

        :default: 256

        :stability: experimental
        '''
        result = self._values.get("maxv_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minv_cpus(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum number of EC2 vCPUs that an environment should maintain (even if the compute environment state is DISABLED).

        Each vCPU is equivalent to 1,024 CPU shares. By keeping this set to 0 you will not have instance time wasted when
        there is no work to be run. If you set this above zero you will maintain that number of vCPUs at all times.

        :default: 0

        :stability: experimental
        '''
        result = self._values.get("minv_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def placement_group(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Amazon EC2 placement group to associate with your compute resources.

        :default: - No placement group will be used.

        :stability: experimental
        '''
        result = self._values.get("placement_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        '''(experimental) The EC2 security group(s) associated with instances launched in the compute environment.

        :default: - AWS default security group.

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def spot_fleet_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) This property will be ignored if you set the environment type to ON_DEMAND.

        The Amazon Resource Name (ARN) of the Amazon EC2 Spot Fleet IAM role applied to a SPOT compute environment.
        For more information, see Amazon EC2 Spot Fleet Role in the AWS Batch User Guide.

        :default: - no fleet role will be used.

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/spot_fleet_IAM_role.html
        '''
        result = self._values.get("spot_fleet_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def type(self) -> typing.Optional[ComputeResourceType]:
        '''(experimental) The type of compute environment: ON_DEMAND, SPOT, FARGATE, or FARGATE_SPOT.

        :default: ON_DEMAND

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[ComputeResourceType], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''(experimental) The VPC subnets into which the compute resources are launched.

        :default: - private subnets of the supplied VPC.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExposedSecret(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch-alpha.ExposedSecret",
):
    '''(experimental) Exposed secret for log configuration.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_ssm as ssm
        
        
        batch.JobDefinition(self, "job-def",
            container=batch.JobDefinitionContainer(
                image=ecs.EcrImage.from_registry("docker/whalesay"),
                log_configuration=batch.LogConfiguration(
                    log_driver=batch.LogDriver.AWSLOGS,
                    options={"awslogs-region": "us-east-1"},
                    secret_options=[
                        batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
                    ]
                )
            )
        )
    '''

    def __init__(self, option_name: builtins.str, secret_arn: builtins.str) -> None:
        '''
        :param option_name: -
        :param secret_arn: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [option_name, secret_arn])

    @jsii.member(jsii_name="fromParametersStore") # type: ignore[misc]
    @builtins.classmethod
    def from_parameters_store(
        cls,
        option_name: builtins.str,
        parameter: aws_cdk.aws_ssm.IParameter,
    ) -> "ExposedSecret":
        '''(experimental) User Parameters Store Parameter.

        :param option_name: - The name of the option.
        :param parameter: - A parameter from parameters store.

        :stability: experimental
        '''
        return typing.cast("ExposedSecret", jsii.sinvoke(cls, "fromParametersStore", [option_name, parameter]))

    @jsii.member(jsii_name="fromSecretsManager") # type: ignore[misc]
    @builtins.classmethod
    def from_secrets_manager(
        cls,
        option_name: builtins.str,
        secret: aws_cdk.aws_secretsmanager.ISecret,
    ) -> "ExposedSecret":
        '''(experimental) Use Secrets Manager Secret.

        :param option_name: - The name of the option.
        :param secret: - A secret from secrets manager.

        :stability: experimental
        '''
        return typing.cast("ExposedSecret", jsii.sinvoke(cls, "fromSecretsManager", [option_name, secret]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionName")
    def option_name(self) -> builtins.str:
        '''(experimental) Name of the option.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "optionName"))

    @option_name.setter
    def option_name(self, value: builtins.str) -> None:
        jsii.set(self, "optionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> builtins.str:
        '''(experimental) ARN of the secret option.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretArn"))

    @secret_arn.setter
    def secret_arn(self, value: builtins.str) -> None:
        jsii.set(self, "secretArn", value)


@jsii.interface(jsii_type="@aws-cdk/aws-batch-alpha.IComputeEnvironment")
class IComputeEnvironment(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) Properties of a compute environment.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentArn")
    def compute_environment_arn(self) -> builtins.str:
        '''(experimental) The ARN of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        '''(experimental) The name of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IComputeEnvironmentProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) Properties of a compute environment.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch-alpha.IComputeEnvironment"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentArn")
    def compute_environment_arn(self) -> builtins.str:
        '''(experimental) The ARN of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        '''(experimental) The name of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IComputeEnvironment).__jsii_proxy_class__ = lambda : _IComputeEnvironmentProxy


@jsii.interface(jsii_type="@aws-cdk/aws-batch-alpha.IJobDefinition")
class IJobDefinition(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) An interface representing a job definition - either a new one, created with the CDK, *using the {@link JobDefinition} class, or existing ones, referenced using the {@link JobDefinition.fromJobDefinitionArn} method.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionArn")
    def job_definition_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job definition.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> builtins.str:
        '''(experimental) The name of the batch job definition.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IJobDefinitionProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) An interface representing a job definition - either a new one, created with the CDK, *using the {@link JobDefinition} class, or existing ones, referenced using the {@link JobDefinition.fromJobDefinitionArn} method.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch-alpha.IJobDefinition"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionArn")
    def job_definition_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job definition.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobDefinitionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> builtins.str:
        '''(experimental) The name of the batch job definition.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobDefinitionName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJobDefinition).__jsii_proxy_class__ = lambda : _IJobDefinitionProxy


@jsii.interface(jsii_type="@aws-cdk/aws-batch-alpha.IJobQueue")
class IJobQueue(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) Properties of a Job Queue.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueArn")
    def job_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job queue.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueName")
    def job_queue_name(self) -> builtins.str:
        '''(experimental) A name for the job queue.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IJobQueueProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) Properties of a Job Queue.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch-alpha.IJobQueue"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueArn")
    def job_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job queue.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobQueueArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueName")
    def job_queue_name(self) -> builtins.str:
        '''(experimental) A name for the job queue.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobQueueName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJobQueue).__jsii_proxy_class__ = lambda : _IJobQueueProxy


@jsii.interface(jsii_type="@aws-cdk/aws-batch-alpha.IMultiNodeProps")
class IMultiNodeProps(typing_extensions.Protocol):
    '''(experimental) Properties for specifying multi-node properties for compute resources.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        '''(experimental) The number of nodes associated with a multi-node parallel job.

        :stability: experimental
        '''
        ...

    @count.setter
    def count(self, value: jsii.Number) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mainNode")
    def main_node(self) -> jsii.Number:
        '''(experimental) Specifies the node index for the main node of a multi-node parallel job.

        This node index value must be fewer than the number of nodes.

        :stability: experimental
        '''
        ...

    @main_node.setter
    def main_node(self, value: jsii.Number) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeProps")
    def range_props(self) -> typing.List["INodeRangeProps"]:
        '''(experimental) A list of node ranges and their properties associated with a multi-node parallel job.

        :stability: experimental
        '''
        ...

    @range_props.setter
    def range_props(self, value: typing.List["INodeRangeProps"]) -> None:
        ...


class _IMultiNodePropsProxy:
    '''(experimental) Properties for specifying multi-node properties for compute resources.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch-alpha.IMultiNodeProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="count")
    def count(self) -> jsii.Number:
        '''(experimental) The number of nodes associated with a multi-node parallel job.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "count"))

    @count.setter
    def count(self, value: jsii.Number) -> None:
        jsii.set(self, "count", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mainNode")
    def main_node(self) -> jsii.Number:
        '''(experimental) Specifies the node index for the main node of a multi-node parallel job.

        This node index value must be fewer than the number of nodes.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "mainNode"))

    @main_node.setter
    def main_node(self, value: jsii.Number) -> None:
        jsii.set(self, "mainNode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rangeProps")
    def range_props(self) -> typing.List["INodeRangeProps"]:
        '''(experimental) A list of node ranges and their properties associated with a multi-node parallel job.

        :stability: experimental
        '''
        return typing.cast(typing.List["INodeRangeProps"], jsii.get(self, "rangeProps"))

    @range_props.setter
    def range_props(self, value: typing.List["INodeRangeProps"]) -> None:
        jsii.set(self, "rangeProps", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMultiNodeProps).__jsii_proxy_class__ = lambda : _IMultiNodePropsProxy


@jsii.interface(jsii_type="@aws-cdk/aws-batch-alpha.INodeRangeProps")
class INodeRangeProps(typing_extensions.Protocol):
    '''(experimental) Properties for a multi-node batch job.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="container")
    def container(self) -> "JobDefinitionContainer":
        '''(experimental) The container details for the node range.

        :stability: experimental
        '''
        ...

    @container.setter
    def container(self, value: "JobDefinitionContainer") -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromNodeIndex")
    def from_node_index(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum node index value to apply this container definition against.

        You may nest node ranges, for example 0:10 and 4:5, in which case the 4:5 range properties override the 0:10 properties.

        :default: 0

        :stability: experimental
        '''
        ...

    @from_node_index.setter
    def from_node_index(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toNodeIndex")
    def to_node_index(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum node index value to apply this container definition against. If omitted, the highest value is used relative.

        to the number of nodes associated with the job. You may nest node ranges, for example 0:10 and 4:5,
        in which case the 4:5 range properties override the 0:10 properties.

        :default: {@link IMultiNodeprops.count}

        :stability: experimental
        '''
        ...

    @to_node_index.setter
    def to_node_index(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _INodeRangePropsProxy:
    '''(experimental) Properties for a multi-node batch job.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-batch-alpha.INodeRangeProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="container")
    def container(self) -> "JobDefinitionContainer":
        '''(experimental) The container details for the node range.

        :stability: experimental
        '''
        return typing.cast("JobDefinitionContainer", jsii.get(self, "container"))

    @container.setter
    def container(self, value: "JobDefinitionContainer") -> None:
        jsii.set(self, "container", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromNodeIndex")
    def from_node_index(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum node index value to apply this container definition against.

        You may nest node ranges, for example 0:10 and 4:5, in which case the 4:5 range properties override the 0:10 properties.

        :default: 0

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "fromNodeIndex"))

    @from_node_index.setter
    def from_node_index(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "fromNodeIndex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toNodeIndex")
    def to_node_index(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum node index value to apply this container definition against. If omitted, the highest value is used relative.

        to the number of nodes associated with the job. You may nest node ranges, for example 0:10 and 4:5,
        in which case the 4:5 range properties override the 0:10 properties.

        :default: {@link IMultiNodeprops.count}

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "toNodeIndex"))

    @to_node_index.setter
    def to_node_index(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "toNodeIndex", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INodeRangeProps).__jsii_proxy_class__ = lambda : _INodeRangePropsProxy


@jsii.implements(IJobDefinition)
class JobDefinition(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch-alpha.JobDefinition",
):
    '''(experimental) Batch Job Definition.

    Defines a batch job definition to execute a specific batch job.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_ecr as ecr
        
        
        repo = ecr.Repository.from_repository_name(self, "batch-job-repo", "todo-list")
        
        batch.JobDefinition(self, "batch-job-def-from-ecr",
            container=batch.JobDefinitionContainer(
                image=ecs.EcrImage(repo, "latest")
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        container: "JobDefinitionContainer",
        job_definition_name: typing.Optional[builtins.str] = None,
        node_props: typing.Optional[IMultiNodeProps] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        platform_capabilities: typing.Optional[typing.Sequence["PlatformCapabilities"]] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param container: (experimental) An object with various properties specific to container-based jobs.
        :param job_definition_name: (experimental) The name of the job definition. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: Cloudformation-generated name
        :param node_props: (experimental) An object with various properties specific to multi-node parallel jobs. Default: - undefined
        :param parameters: (experimental) When you submit a job, you can specify parameters that should replace the placeholders or override the default job definition parameters. Parameters in job submission requests take precedence over the defaults in a job definition. This allows you to use the same job definition for multiple jobs that use the same format, and programmatically change values in the command at submission time. Default: - undefined
        :param platform_capabilities: (experimental) The platform capabilities required by the job definition. Default: - EC2
        :param retry_attempts: (experimental) The number of times to move a job to the RUNNABLE status. You may specify between 1 and 10 attempts. If the value of attempts is greater than one, the job is retried on failure the same number of attempts as the value. Default: 1
        :param timeout: (experimental) The timeout configuration for jobs that are submitted with this job definition. You can specify a timeout duration after which AWS Batch terminates your jobs if they have not finished. Default: - undefined

        :stability: experimental
        '''
        props = JobDefinitionProps(
            container=container,
            job_definition_name=job_definition_name,
            node_props=node_props,
            parameters=parameters,
            platform_capabilities=platform_capabilities,
            retry_attempts=retry_attempts,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromJobDefinitionArn") # type: ignore[misc]
    @builtins.classmethod
    def from_job_definition_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        job_definition_arn: builtins.str,
    ) -> IJobDefinition:
        '''(experimental) Imports an existing batch job definition by its amazon resource name.

        :param scope: -
        :param id: -
        :param job_definition_arn: -

        :stability: experimental
        '''
        return typing.cast(IJobDefinition, jsii.sinvoke(cls, "fromJobDefinitionArn", [scope, id, job_definition_arn]))

    @jsii.member(jsii_name="fromJobDefinitionName") # type: ignore[misc]
    @builtins.classmethod
    def from_job_definition_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        job_definition_name: builtins.str,
    ) -> IJobDefinition:
        '''(experimental) Imports an existing batch job definition by its name.

        If name is specified without a revision then the latest active revision is used.

        :param scope: -
        :param id: -
        :param job_definition_name: -

        :stability: experimental
        '''
        return typing.cast(IJobDefinition, jsii.sinvoke(cls, "fromJobDefinitionName", [scope, id, job_definition_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionArn")
    def job_definition_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job definition.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobDefinitionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobDefinitionName")
    def job_definition_name(self) -> builtins.str:
        '''(experimental) The name of the batch job definition.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobDefinitionName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch-alpha.JobDefinitionContainer",
    jsii_struct_bases=[],
    name_mapping={
        "image": "image",
        "assign_public_ip": "assignPublicIp",
        "command": "command",
        "environment": "environment",
        "execution_role": "executionRole",
        "gpu_count": "gpuCount",
        "instance_type": "instanceType",
        "job_role": "jobRole",
        "linux_params": "linuxParams",
        "log_configuration": "logConfiguration",
        "memory_limit_mib": "memoryLimitMiB",
        "mount_points": "mountPoints",
        "platform_version": "platformVersion",
        "privileged": "privileged",
        "read_only": "readOnly",
        "ulimits": "ulimits",
        "user": "user",
        "vcpus": "vcpus",
        "volumes": "volumes",
    },
)
class JobDefinitionContainer:
    def __init__(
        self,
        *,
        image: aws_cdk.aws_ecs.ContainerImage,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        execution_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        gpu_count: typing.Optional[jsii.Number] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        job_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        linux_params: typing.Optional[aws_cdk.aws_ecs.LinuxParameters] = None,
        log_configuration: typing.Optional["LogConfiguration"] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        mount_points: typing.Optional[typing.Sequence[aws_cdk.aws_ecs.MountPoint]] = None,
        platform_version: typing.Optional[aws_cdk.aws_ecs.FargatePlatformVersion] = None,
        privileged: typing.Optional[builtins.bool] = None,
        read_only: typing.Optional[builtins.bool] = None,
        ulimits: typing.Optional[typing.Sequence[aws_cdk.aws_ecs.Ulimit]] = None,
        user: typing.Optional[builtins.str] = None,
        vcpus: typing.Optional[jsii.Number] = None,
        volumes: typing.Optional[typing.Sequence[aws_cdk.aws_ecs.Volume]] = None,
    ) -> None:
        '''(experimental) Properties of a job definition container.

        :param image: (experimental) The image used to start a container.
        :param assign_public_ip: (experimental) Whether or not to assign a public IP to the job. Default: - false
        :param command: (experimental) The command that is passed to the container. If you provide a shell command as a single string, you have to quote command-line arguments. Default: - CMD value built into container image.
        :param environment: (experimental) The environment variables to pass to the container. Default: none
        :param execution_role: (experimental) The IAM role that AWS Batch can assume. Required when using Fargate. Default: - None
        :param gpu_count: (experimental) The number of physical GPUs to reserve for the container. The number of GPUs reserved for all containers in a job should not exceed the number of available GPUs on the compute resource that the job is launched on. Default: - No GPU reservation.
        :param instance_type: (experimental) The instance type to use for a multi-node parallel job. Currently all node groups in a multi-node parallel job must use the same instance type. This parameter is not valid for single-node container jobs. Default: - None
        :param job_role: (experimental) The IAM role that the container can assume for AWS permissions. Default: - An IAM role will created.
        :param linux_params: (experimental) Linux-specific modifications that are applied to the container, such as details for device mappings. For now, only the ``devices`` property is supported. Default: - None will be used.
        :param log_configuration: (experimental) The log configuration specification for the container. Default: - containers use the same logging driver that the Docker daemon uses
        :param memory_limit_mib: (experimental) The hard limit (in MiB) of memory to present to the container. If your container attempts to exceed the memory specified here, the container is killed. You must specify at least 4 MiB of memory for EC2 and 512 MiB for Fargate. Default: - 4 for EC2, 512 for Fargate
        :param mount_points: (experimental) The mount points for data volumes in your container. Default: - No mount points will be used.
        :param platform_version: (experimental) Fargate platform version. Default: - LATEST platform version will be used
        :param privileged: (experimental) When this parameter is true, the container is given elevated privileges on the host container instance (similar to the root user). Default: false
        :param read_only: (experimental) When this parameter is true, the container is given read-only access to its root file system. Default: false
        :param ulimits: (experimental) A list of ulimits to set in the container. Default: - No limits.
        :param user: (experimental) The user name to use inside the container. Default: - None will be used.
        :param vcpus: (experimental) The number of vCPUs reserved for the container. Each vCPU is equivalent to 1,024 CPU shares. You must specify at least one vCPU for EC2 and 0.25 for Fargate. Default: - 1 for EC2, 0.25 for Fargate
        :param volumes: (experimental) A list of data volumes used in a job. Default: - No data volumes will be used.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ecr as ecr
            
            
            repo = ecr.Repository.from_repository_name(self, "batch-job-repo", "todo-list")
            
            batch.JobDefinition(self, "batch-job-def-from-ecr",
                container=batch.JobDefinitionContainer(
                    image=ecs.EcrImage(repo, "latest")
                )
            )
        '''
        if isinstance(log_configuration, dict):
            log_configuration = LogConfiguration(**log_configuration)
        self._values: typing.Dict[str, typing.Any] = {
            "image": image,
        }
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if command is not None:
            self._values["command"] = command
        if environment is not None:
            self._values["environment"] = environment
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if gpu_count is not None:
            self._values["gpu_count"] = gpu_count
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if job_role is not None:
            self._values["job_role"] = job_role
        if linux_params is not None:
            self._values["linux_params"] = linux_params
        if log_configuration is not None:
            self._values["log_configuration"] = log_configuration
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if mount_points is not None:
            self._values["mount_points"] = mount_points
        if platform_version is not None:
            self._values["platform_version"] = platform_version
        if privileged is not None:
            self._values["privileged"] = privileged
        if read_only is not None:
            self._values["read_only"] = read_only
        if ulimits is not None:
            self._values["ulimits"] = ulimits
        if user is not None:
            self._values["user"] = user
        if vcpus is not None:
            self._values["vcpus"] = vcpus
        if volumes is not None:
            self._values["volumes"] = volumes

    @builtins.property
    def image(self) -> aws_cdk.aws_ecs.ContainerImage:
        '''(experimental) The image used to start a container.

        :stability: experimental
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(aws_cdk.aws_ecs.ContainerImage, result)

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not to assign a public IP to the job.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The command that is passed to the container.

        If you provide a shell command as a single string, you have to quote command-line arguments.

        :default: - CMD value built into container image.

        :stability: experimental
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The environment variables to pass to the container.

        :default: none

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def execution_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM role that AWS Batch can assume.

        Required when using Fargate.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def gpu_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of physical GPUs to reserve for the container.

        The number of GPUs reserved for all
        containers in a job should not exceed the number of available GPUs on the compute resource that the job is launched on.

        :default: - No GPU reservation.

        :stability: experimental
        '''
        result = self._values.get("gpu_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''(experimental) The instance type to use for a multi-node parallel job.

        Currently all node groups in a
        multi-node parallel job must use the same instance type. This parameter is not valid
        for single-node container jobs.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def job_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM role that the container can assume for AWS permissions.

        :default: - An IAM role will created.

        :stability: experimental
        '''
        result = self._values.get("job_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def linux_params(self) -> typing.Optional[aws_cdk.aws_ecs.LinuxParameters]:
        '''(experimental) Linux-specific modifications that are applied to the container, such as details for device mappings.

        For now, only the ``devices`` property is supported.

        :default: - None will be used.

        :stability: experimental
        '''
        result = self._values.get("linux_params")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.LinuxParameters], result)

    @builtins.property
    def log_configuration(self) -> typing.Optional["LogConfiguration"]:
        '''(experimental) The log configuration specification for the container.

        :default: - containers use the same logging driver that the Docker daemon uses

        :stability: experimental
        '''
        result = self._values.get("log_configuration")
        return typing.cast(typing.Optional["LogConfiguration"], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The hard limit (in MiB) of memory to present to the container.

        If your container attempts to exceed
        the memory specified here, the container is killed. You must specify at least 4 MiB of memory for EC2 and 512 MiB for Fargate.

        :default: - 4 for EC2, 512 for Fargate

        :stability: experimental
        '''
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mount_points(self) -> typing.Optional[typing.List[aws_cdk.aws_ecs.MountPoint]]:
        '''(experimental) The mount points for data volumes in your container.

        :default: - No mount points will be used.

        :stability: experimental
        '''
        result = self._values.get("mount_points")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ecs.MountPoint]], result)

    @builtins.property
    def platform_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_ecs.FargatePlatformVersion]:
        '''(experimental) Fargate platform version.

        :default: - LATEST platform version will be used

        :stability: experimental
        '''
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.FargatePlatformVersion], result)

    @builtins.property
    def privileged(self) -> typing.Optional[builtins.bool]:
        '''(experimental) When this parameter is true, the container is given elevated privileges on the host container instance (similar to the root user).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("privileged")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''(experimental) When this parameter is true, the container is given read-only access to its root file system.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ulimits(self) -> typing.Optional[typing.List[aws_cdk.aws_ecs.Ulimit]]:
        '''(experimental) A list of ulimits to set in the container.

        :default: - No limits.

        :stability: experimental
        '''
        result = self._values.get("ulimits")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ecs.Ulimit]], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''(experimental) The user name to use inside the container.

        :default: - None will be used.

        :stability: experimental
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vcpus(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of vCPUs reserved for the container.

        Each vCPU is equivalent to
        1,024 CPU shares. You must specify at least one vCPU for EC2 and 0.25 for Fargate.

        :default: - 1 for EC2, 0.25 for Fargate

        :stability: experimental
        '''
        result = self._values.get("vcpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List[aws_cdk.aws_ecs.Volume]]:
        '''(experimental) A list of data volumes used in a job.

        :default: - No data volumes will be used.

        :stability: experimental
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ecs.Volume]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobDefinitionContainer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch-alpha.JobDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={
        "container": "container",
        "job_definition_name": "jobDefinitionName",
        "node_props": "nodeProps",
        "parameters": "parameters",
        "platform_capabilities": "platformCapabilities",
        "retry_attempts": "retryAttempts",
        "timeout": "timeout",
    },
)
class JobDefinitionProps:
    def __init__(
        self,
        *,
        container: JobDefinitionContainer,
        job_definition_name: typing.Optional[builtins.str] = None,
        node_props: typing.Optional[IMultiNodeProps] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        platform_capabilities: typing.Optional[typing.Sequence["PlatformCapabilities"]] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link JobDefinition} construct.

        :param container: (experimental) An object with various properties specific to container-based jobs.
        :param job_definition_name: (experimental) The name of the job definition. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: Cloudformation-generated name
        :param node_props: (experimental) An object with various properties specific to multi-node parallel jobs. Default: - undefined
        :param parameters: (experimental) When you submit a job, you can specify parameters that should replace the placeholders or override the default job definition parameters. Parameters in job submission requests take precedence over the defaults in a job definition. This allows you to use the same job definition for multiple jobs that use the same format, and programmatically change values in the command at submission time. Default: - undefined
        :param platform_capabilities: (experimental) The platform capabilities required by the job definition. Default: - EC2
        :param retry_attempts: (experimental) The number of times to move a job to the RUNNABLE status. You may specify between 1 and 10 attempts. If the value of attempts is greater than one, the job is retried on failure the same number of attempts as the value. Default: 1
        :param timeout: (experimental) The timeout configuration for jobs that are submitted with this job definition. You can specify a timeout duration after which AWS Batch terminates your jobs if they have not finished. Default: - undefined

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ecr as ecr
            
            
            repo = ecr.Repository.from_repository_name(self, "batch-job-repo", "todo-list")
            
            batch.JobDefinition(self, "batch-job-def-from-ecr",
                container=batch.JobDefinitionContainer(
                    image=ecs.EcrImage(repo, "latest")
                )
            )
        '''
        if isinstance(container, dict):
            container = JobDefinitionContainer(**container)
        self._values: typing.Dict[str, typing.Any] = {
            "container": container,
        }
        if job_definition_name is not None:
            self._values["job_definition_name"] = job_definition_name
        if node_props is not None:
            self._values["node_props"] = node_props
        if parameters is not None:
            self._values["parameters"] = parameters
        if platform_capabilities is not None:
            self._values["platform_capabilities"] = platform_capabilities
        if retry_attempts is not None:
            self._values["retry_attempts"] = retry_attempts
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def container(self) -> JobDefinitionContainer:
        '''(experimental) An object with various properties specific to container-based jobs.

        :stability: experimental
        '''
        result = self._values.get("container")
        assert result is not None, "Required property 'container' is missing"
        return typing.cast(JobDefinitionContainer, result)

    @builtins.property
    def job_definition_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the job definition.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :default: Cloudformation-generated name

        :stability: experimental
        '''
        result = self._values.get("job_definition_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_props(self) -> typing.Optional[IMultiNodeProps]:
        '''(experimental) An object with various properties specific to multi-node parallel jobs.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("node_props")
        return typing.cast(typing.Optional[IMultiNodeProps], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) When you submit a job, you can specify parameters that should replace the placeholders or override the default job definition parameters.

        Parameters
        in job submission requests take precedence over the defaults in a job definition.
        This allows you to use the same job definition for multiple jobs that use the same
        format, and programmatically change values in the command at submission time.

        :default: - undefined

        :stability: experimental
        :link: https://docs.aws.amazon.com/batch/latest/userguide/job_definition_parameters.html
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def platform_capabilities(
        self,
    ) -> typing.Optional[typing.List["PlatformCapabilities"]]:
        '''(experimental) The platform capabilities required by the job definition.

        :default: - EC2

        :stability: experimental
        '''
        result = self._values.get("platform_capabilities")
        return typing.cast(typing.Optional[typing.List["PlatformCapabilities"]], result)

    @builtins.property
    def retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of times to move a job to the RUNNABLE status.

        You may specify between 1 and
        10 attempts. If the value of attempts is greater than one, the job is retried on failure
        the same number of attempts as the value.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) The timeout configuration for jobs that are submitted with this job definition.

        You can specify
        a timeout duration after which AWS Batch terminates your jobs if they have not finished.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IJobQueue)
class JobQueue(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch-alpha.JobQueue",
):
    '''(experimental) Batch Job Queue.

    Defines a batch job queue to define how submitted batch jobs
    should be ran based on specified batch compute environments.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # compute_environment: batch.ComputeEnvironment
        
        job_queue = batch.JobQueue(self, "JobQueue",
            compute_environments=[batch.JobQueueComputeEnvironment(
                # Defines a collection of compute resources to handle assigned batch jobs
                compute_environment=compute_environment,
                # Order determines the allocation order for jobs (i.e. Lower means higher preference for job assignment)
                order=1
            )
            ]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        compute_environments: typing.Sequence["JobQueueComputeEnvironment"],
        enabled: typing.Optional[builtins.bool] = None,
        job_queue_name: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param compute_environments: (experimental) The set of compute environments mapped to a job queue and their order relative to each other. The job scheduler uses this parameter to determine which compute environment should execute a given job. Compute environments must be in the VALID state before you can associate them with a job queue. You can associate up to three compute environments with a job queue.
        :param enabled: (experimental) The state of the job queue. If set to true, it is able to accept jobs. Default: true
        :param job_queue_name: (experimental) A name for the job queue. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: - Cloudformation-generated name
        :param priority: (experimental) The priority of the job queue. Job queues with a higher priority (or a higher integer value for the priority parameter) are evaluated first when associated with the same compute environment. Priority is determined in descending order, for example, a job queue with a priority value of 10 is given scheduling preference over a job queue with a priority value of 1. Default: 1

        :stability: experimental
        '''
        props = JobQueueProps(
            compute_environments=compute_environments,
            enabled=enabled,
            job_queue_name=job_queue_name,
            priority=priority,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromJobQueueArn") # type: ignore[misc]
    @builtins.classmethod
    def from_job_queue_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        job_queue_arn: builtins.str,
    ) -> IJobQueue:
        '''(experimental) Fetches an existing batch job queue by its amazon resource name.

        :param scope: -
        :param id: -
        :param job_queue_arn: -

        :stability: experimental
        '''
        return typing.cast(IJobQueue, jsii.sinvoke(cls, "fromJobQueueArn", [scope, id, job_queue_arn]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueArn")
    def job_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of this batch job queue.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobQueueArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobQueueName")
    def job_queue_name(self) -> builtins.str:
        '''(experimental) A name for the job queue.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobQueueName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch-alpha.JobQueueComputeEnvironment",
    jsii_struct_bases=[],
    name_mapping={"compute_environment": "computeEnvironment", "order": "order"},
)
class JobQueueComputeEnvironment:
    def __init__(
        self,
        *,
        compute_environment: IComputeEnvironment,
        order: jsii.Number,
    ) -> None:
        '''(experimental) Properties for mapping a compute environment to a job queue.

        :param compute_environment: (experimental) The batch compute environment to use for processing submitted jobs to this queue.
        :param order: (experimental) The order in which this compute environment will be selected for dynamic allocation of resources to process submitted jobs.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_batch_alpha as batch_alpha
            
            # compute_environment: batch_alpha.ComputeEnvironment
            
            job_queue_compute_environment = batch_alpha.JobQueueComputeEnvironment(
                compute_environment=compute_environment,
                order=123
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "compute_environment": compute_environment,
            "order": order,
        }

    @builtins.property
    def compute_environment(self) -> IComputeEnvironment:
        '''(experimental) The batch compute environment to use for processing submitted jobs to this queue.

        :stability: experimental
        '''
        result = self._values.get("compute_environment")
        assert result is not None, "Required property 'compute_environment' is missing"
        return typing.cast(IComputeEnvironment, result)

    @builtins.property
    def order(self) -> jsii.Number:
        '''(experimental) The order in which this compute environment will be selected for dynamic allocation of resources to process submitted jobs.

        :stability: experimental
        '''
        result = self._values.get("order")
        assert result is not None, "Required property 'order' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobQueueComputeEnvironment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch-alpha.JobQueueProps",
    jsii_struct_bases=[],
    name_mapping={
        "compute_environments": "computeEnvironments",
        "enabled": "enabled",
        "job_queue_name": "jobQueueName",
        "priority": "priority",
    },
)
class JobQueueProps:
    def __init__(
        self,
        *,
        compute_environments: typing.Sequence[JobQueueComputeEnvironment],
        enabled: typing.Optional[builtins.bool] = None,
        job_queue_name: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties of a batch job queue.

        :param compute_environments: (experimental) The set of compute environments mapped to a job queue and their order relative to each other. The job scheduler uses this parameter to determine which compute environment should execute a given job. Compute environments must be in the VALID state before you can associate them with a job queue. You can associate up to three compute environments with a job queue.
        :param enabled: (experimental) The state of the job queue. If set to true, it is able to accept jobs. Default: true
        :param job_queue_name: (experimental) A name for the job queue. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: - Cloudformation-generated name
        :param priority: (experimental) The priority of the job queue. Job queues with a higher priority (or a higher integer value for the priority parameter) are evaluated first when associated with the same compute environment. Priority is determined in descending order, for example, a job queue with a priority value of 10 is given scheduling preference over a job queue with a priority value of 1. Default: 1

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # compute_environment: batch.ComputeEnvironment
            
            job_queue = batch.JobQueue(self, "JobQueue",
                compute_environments=[batch.JobQueueComputeEnvironment(
                    # Defines a collection of compute resources to handle assigned batch jobs
                    compute_environment=compute_environment,
                    # Order determines the allocation order for jobs (i.e. Lower means higher preference for job assignment)
                    order=1
                )
                ]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "compute_environments": compute_environments,
        }
        if enabled is not None:
            self._values["enabled"] = enabled
        if job_queue_name is not None:
            self._values["job_queue_name"] = job_queue_name
        if priority is not None:
            self._values["priority"] = priority

    @builtins.property
    def compute_environments(self) -> typing.List[JobQueueComputeEnvironment]:
        '''(experimental) The set of compute environments mapped to a job queue and their order relative to each other.

        The job scheduler uses this parameter to
        determine which compute environment should execute a given job. Compute environments must be in the VALID state before you can associate them
        with a job queue. You can associate up to three compute environments with a job queue.

        :stability: experimental
        '''
        result = self._values.get("compute_environments")
        assert result is not None, "Required property 'compute_environments' is missing"
        return typing.cast(typing.List[JobQueueComputeEnvironment], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The state of the job queue.

        If set to true, it is able to accept jobs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def job_queue_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the job queue.

        Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed.

        :default: - Cloudformation-generated name

        :stability: experimental
        '''
        result = self._values.get("job_queue_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The priority of the job queue.

        Job queues with a higher priority (or a higher integer value for the priority parameter) are evaluated first
        when associated with the same compute environment. Priority is determined in descending order, for example, a job queue with a priority value
        of 10 is given scheduling preference over a job queue with a priority value of 1.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobQueueProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch-alpha.LaunchTemplateSpecification",
    jsii_struct_bases=[],
    name_mapping={"launch_template_name": "launchTemplateName", "version": "version"},
)
class LaunchTemplateSpecification:
    def __init__(
        self,
        *,
        launch_template_name: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Launch template property specification.

        :param launch_template_name: (experimental) The Launch template name.
        :param version: (experimental) The launch template version to be used (optional). Default: - the default version of the launch template

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            # my_launch_template: ec2.CfnLaunchTemplate
            
            
            my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
                compute_resources=batch.ComputeResources(
                    launch_template=batch.LaunchTemplateSpecification(
                        launch_template_name=my_launch_template.launch_template_name
                    ),
                    vpc=vpc
                ),
                compute_environment_name="MyStorageCapableComputeEnvironment"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "launch_template_name": launch_template_name,
        }
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def launch_template_name(self) -> builtins.str:
        '''(experimental) The Launch template name.

        :stability: experimental
        '''
        result = self._values.get("launch_template_name")
        assert result is not None, "Required property 'launch_template_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The launch template version to be used (optional).

        :default: - the default version of the launch template

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LaunchTemplateSpecification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-batch-alpha.LogConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "log_driver": "logDriver",
        "options": "options",
        "secret_options": "secretOptions",
    },
)
class LogConfiguration:
    def __init__(
        self,
        *,
        log_driver: "LogDriver",
        options: typing.Any = None,
        secret_options: typing.Optional[typing.Sequence[ExposedSecret]] = None,
    ) -> None:
        '''(experimental) Log configuration options to send to a custom log driver for the container.

        :param log_driver: (experimental) The log driver to use for the container.
        :param options: (experimental) The configuration options to send to the log driver. Default: - No configuration options are sent
        :param secret_options: (experimental) The secrets to pass to the log configuration as options. For more information, see https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data-secrets.html#secrets-logconfig Default: - No secrets are passed

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ssm as ssm
            
            
            batch.JobDefinition(self, "job-def",
                container=batch.JobDefinitionContainer(
                    image=ecs.EcrImage.from_registry("docker/whalesay"),
                    log_configuration=batch.LogConfiguration(
                        log_driver=batch.LogDriver.AWSLOGS,
                        options={"awslogs-region": "us-east-1"},
                        secret_options=[
                            batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
                        ]
                    )
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_driver": log_driver,
        }
        if options is not None:
            self._values["options"] = options
        if secret_options is not None:
            self._values["secret_options"] = secret_options

    @builtins.property
    def log_driver(self) -> "LogDriver":
        '''(experimental) The log driver to use for the container.

        :stability: experimental
        '''
        result = self._values.get("log_driver")
        assert result is not None, "Required property 'log_driver' is missing"
        return typing.cast("LogDriver", result)

    @builtins.property
    def options(self) -> typing.Any:
        '''(experimental) The configuration options to send to the log driver.

        :default: - No configuration options are sent

        :stability: experimental
        '''
        result = self._values.get("options")
        return typing.cast(typing.Any, result)

    @builtins.property
    def secret_options(self) -> typing.Optional[typing.List[ExposedSecret]]:
        '''(experimental) The secrets to pass to the log configuration as options.

        For more information, see https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data-secrets.html#secrets-logconfig

        :default: - No secrets are passed

        :stability: experimental
        '''
        result = self._values.get("secret_options")
        return typing.cast(typing.Optional[typing.List[ExposedSecret]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-batch-alpha.LogDriver")
class LogDriver(enum.Enum):
    '''(experimental) The log driver to use for the container.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_ssm as ssm
        
        
        batch.JobDefinition(self, "job-def",
            container=batch.JobDefinitionContainer(
                image=ecs.EcrImage.from_registry("docker/whalesay"),
                log_configuration=batch.LogConfiguration(
                    log_driver=batch.LogDriver.AWSLOGS,
                    options={"awslogs-region": "us-east-1"},
                    secret_options=[
                        batch.ExposedSecret.from_parameters_store("xyz", ssm.StringParameter.from_string_parameter_name(self, "parameter", "xyz"))
                    ]
                )
            )
        )
    '''

    AWSLOGS = "AWSLOGS"
    '''(experimental) Specifies the Amazon CloudWatch Logs logging driver.

    :stability: experimental
    '''
    FLUENTD = "FLUENTD"
    '''(experimental) Specifies the Fluentd logging driver.

    :stability: experimental
    '''
    GELF = "GELF"
    '''(experimental) Specifies the Graylog Extended Format (GELF) logging driver.

    :stability: experimental
    '''
    JOURNALD = "JOURNALD"
    '''(experimental) Specifies the journald logging driver.

    :stability: experimental
    '''
    LOGENTRIES = "LOGENTRIES"
    '''(experimental) Specifies the logentries logging driver.

    :stability: experimental
    '''
    JSON_FILE = "JSON_FILE"
    '''(experimental) Specifies the JSON file logging driver.

    :stability: experimental
    '''
    SPLUNK = "SPLUNK"
    '''(experimental) Specifies the Splunk logging driver.

    :stability: experimental
    '''
    SYSLOG = "SYSLOG"
    '''(experimental) Specifies the syslog logging driver.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-batch-alpha.PlatformCapabilities")
class PlatformCapabilities(enum.Enum):
    '''(experimental) Platform capabilities.

    :stability: experimental
    '''

    EC2 = "EC2"
    '''(experimental) Specifies EC2 environment.

    :stability: experimental
    '''
    FARGATE = "FARGATE"
    '''(experimental) Specifies Fargate environment.

    :stability: experimental
    '''


@jsii.implements(IComputeEnvironment)
class ComputeEnvironment(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-batch-alpha.ComputeEnvironment",
):
    '''(experimental) Batch Compute Environment.

    Defines a batch compute environment to run batch jobs on.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # vpc: ec2.Vpc
        
        my_compute_env = batch.ComputeEnvironment(self, "ComputeEnv",
            compute_resources=batch.ComputeResources(
                image=ec2.MachineImage.generic_linux({
                    "[aws-region]": "[ami-ID]"
                }),
                vpc=vpc
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        compute_environment_name: typing.Optional[builtins.str] = None,
        compute_resources: typing.Optional[ComputeResources] = None,
        enabled: typing.Optional[builtins.bool] = None,
        managed: typing.Optional[builtins.bool] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param compute_environment_name: (experimental) A name for the compute environment. Up to 128 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. Default: - CloudFormation-generated name
        :param compute_resources: (experimental) The details of the required compute resources for the managed compute environment. If specified, and this is an unmanaged compute environment, will throw an error. By default, AWS Batch managed compute environments use a recent, approved version of the Amazon ECS-optimized AMI for compute resources. Default: - CloudFormation defaults
        :param enabled: (experimental) The state of the compute environment. If the state is set to true, then the compute environment accepts jobs from a queue and can scale out automatically based on queues. Default: true
        :param managed: (experimental) Determines if AWS should manage the allocation of compute resources for processing jobs. If set to false, then you are in charge of providing the compute resource details. Default: true
        :param service_role: (experimental) The IAM role used by Batch to make calls to other AWS services on your behalf for managing the resources that you use with the service. By default, this role is created for you using the AWS managed service policy for Batch. Default: - Role using the 'service-role/AWSBatchServiceRole' policy.

        :stability: experimental
        '''
        props = ComputeEnvironmentProps(
            compute_environment_name=compute_environment_name,
            compute_resources=compute_resources,
            enabled=enabled,
            managed=managed,
            service_role=service_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromComputeEnvironmentArn") # type: ignore[misc]
    @builtins.classmethod
    def from_compute_environment_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        compute_environment_arn: builtins.str,
    ) -> IComputeEnvironment:
        '''(experimental) Fetches an existing batch compute environment by its amazon resource name.

        :param scope: -
        :param id: -
        :param compute_environment_arn: -

        :stability: experimental
        '''
        return typing.cast(IComputeEnvironment, jsii.sinvoke(cls, "fromComputeEnvironmentArn", [scope, id, compute_environment_arn]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentArn")
    def compute_environment_arn(self) -> builtins.str:
        '''(experimental) The ARN of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="computeEnvironmentName")
    def compute_environment_name(self) -> builtins.str:
        '''(experimental) The name of this compute environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "computeEnvironmentName"))


__all__ = [
    "AllocationStrategy",
    "ComputeEnvironment",
    "ComputeEnvironmentProps",
    "ComputeResourceType",
    "ComputeResources",
    "ExposedSecret",
    "IComputeEnvironment",
    "IJobDefinition",
    "IJobQueue",
    "IMultiNodeProps",
    "INodeRangeProps",
    "JobDefinition",
    "JobDefinitionContainer",
    "JobDefinitionProps",
    "JobQueue",
    "JobQueueComputeEnvironment",
    "JobQueueProps",
    "LaunchTemplateSpecification",
    "LogConfiguration",
    "LogDriver",
    "PlatformCapabilities",
]

publication.publish()
