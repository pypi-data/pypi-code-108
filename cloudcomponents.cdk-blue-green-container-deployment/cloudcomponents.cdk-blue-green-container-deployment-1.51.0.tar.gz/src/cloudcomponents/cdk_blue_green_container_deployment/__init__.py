'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-blue-green-container-deployment

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-blue-green-container-deployment)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-blue-green-container-deployment/)
[![Mentioned in Awesome CDK](https://awesome.re/mentioned-badge.svg)](https://github.com/kolomied/awesome-cdk)

> Blue green container deployment with CodeDeploy

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-blue-green-container-deployment
```

Python:

```bash
pip install cloudcomponents.cdk-blue-green-container-deployment
```

## How to use

```python
import { Construct, Duration, Stack, StackProps } from '@aws-cdk/core';
import { Repository } from '@aws-cdk/aws-codecommit';
import { Pipeline, Artifact } from '@aws-cdk/aws-codepipeline';
import { Vpc, Port } from '@aws-cdk/aws-ec2';
import { Cluster } from '@aws-cdk/aws-ecs';
import {
  ApplicationLoadBalancer,
  ApplicationTargetGroup,
  TargetType,
} from '@aws-cdk/aws-elasticloadbalancingv2';
import {
  CodeBuildAction,
  CodeCommitSourceAction,
  CodeDeployEcsDeployAction,
} from '@aws-cdk/aws-codepipeline-actions';

import { ImageRepository } from '@cloudcomponents/cdk-container-registry';
import {
  EcsService,
  DummyTaskDefinition,
  EcsDeploymentConfig,
  EcsDeploymentGroup,
  PushImageProject,
} from '@cloudcomponents/cdk-blue-green-container-deployment';

export class BlueGreenContainerDeploymentStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const vpc = new Vpc(this, 'Vpc', {
      maxAzs: 2,
    });

    const cluster = new Cluster(this, 'Cluster', {
      vpc,
      clusterName: 'blue-green-cluster',
    });

    const loadBalancer = new ApplicationLoadBalancer(this, 'LoadBalancer', {
      vpc,
      internetFacing: true,
    });

    const prodListener = loadBalancer.addListener('ProdListener', {
      port: 80,
    });

    const testListener = loadBalancer.addListener('TestListener', {
      port: 8080,
    });

    const prodTargetGroup = new ApplicationTargetGroup(
      this,
      'ProdTargetGroup',
      {
        port: 80,
        targetType: TargetType.IP,
        vpc,
      },
    );

    prodListener.addTargetGroups('AddProdTg', {
      targetGroups: [prodTargetGroup],
    });

    const testTargetGroup = new ApplicationTargetGroup(
      this,
      'TestTargetGroup',
      {
        port: 8080,
        targetType: TargetType.IP,
        vpc,
      },
    );

    testListener.addTargetGroups('AddTestTg', {
      targetGroups: [testTargetGroup],
    });

    // Will be replaced by CodeDeploy in CodePipeline
    const taskDefinition = new DummyTaskDefinition(
      this,
      'DummyTaskDefinition',
      {
        image: 'nginx',
        family: 'blue-green',
      },
    );

    const ecsService = new EcsService(this, 'EcsService', {
      cluster,
      serviceName: 'blue-green-service',
      desiredCount: 2,
      taskDefinition,
      prodTargetGroup,
      testTargetGroup,
    });

    ecsService.connections.allowFrom(loadBalancer, Port.tcp(80));
    ecsService.connections.allowFrom(loadBalancer, Port.tcp(8080));

    const deploymentConfig = new EcsDeploymentConfig(
      this,
      'DeploymentConfig',
      {
        deploymentConfigName: 'Canary20Percent5Minute',
        trafficRoutingConfig: {
          type: 'TimeBasedCanary',
          timeBasedCanary: {
            canaryInterval: 5,
            canaryPercentage: 20,
          },
        },
      }
    );

    const deploymentGroup = new EcsDeploymentGroup(this, 'DeploymentGroup', {
      applicationName: 'blue-green-application',
      deploymentGroupName: 'blue-green-deployment-group',
      ecsServices: [ecsService],
      targetGroups: [prodTargetGroup, testTargetGroup],
      prodTrafficListener: prodListener,
      testTrafficListener: testListener,
      terminationWaitTime: Duration.minutes(100),
      deploymentConfig, // If you want to use default DeploymentConfig name, use static method as "EcsDeploymentConfig.CANARY_10PERCENT_15MINUTES".
    });

    // @see https://github.com/cloudcomponents/cdk-constructs/tree/master/examples/blue-green-container-deployment-example/blue-green-repository
    const repository = new Repository(this, 'CodeRepository', {
      repositoryName: 'blue-green-repository',
    });

    const imageRepository = new ImageRepository(this, 'ImageRepository', {
      forceDelete: true, //Only for tests
    });

    const sourceArtifact = new Artifact();

    const sourceAction = new CodeCommitSourceAction({
      actionName: 'CodeCommit',
      repository,
      output: sourceArtifact,
    });

    const imageArtifact = new Artifact('ImageArtifact');
    const manifestArtifact = new Artifact('ManifestArtifact');

    const pushImageProject = new PushImageProject(this, 'PushImageProject', {
      imageRepository,
      taskDefinition,
    });

    const buildAction = new CodeBuildAction({
      actionName: 'PushImage',
      project: pushImageProject,
      input: sourceArtifact,
      outputs: [imageArtifact, manifestArtifact],
    });

    const deployAction = new CodeDeployEcsDeployAction({
      actionName: 'CodeDeploy',
      taskDefinitionTemplateInput: manifestArtifact,
      appSpecTemplateInput: manifestArtifact,
      containerImageInputs: [
        {
          input: imageArtifact,
          taskDefinitionPlaceholder: 'IMAGE1_NAME',
        },
      ],
      deploymentGroup,
    });

    new Pipeline(this, 'Pipeline', {
      pipelineName: 'blue-green-pipeline',
      stages: [
        {
          stageName: 'Source',
          actions: [sourceAction],
        },
        {
          stageName: 'Build',
          actions: [buildAction],
        },
        {
          stageName: 'Deploy',
          actions: [deployAction],
        },
      ],
    });
  }
}
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-blue-green-container-deployment/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-blue-green-container-deployment//LICENSE)
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

import aws_cdk.aws_codebuild
import aws_cdk.aws_codedeploy
import aws_cdk.aws_ec2
import aws_cdk.aws_ecr
import aws_cdk.aws_ecs
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_iam
import aws_cdk.core


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.DummyTaskDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={
        "image": "image",
        "container_name": "containerName",
        "container_port": "containerPort",
        "family": "family",
    },
)
class DummyTaskDefinitionProps:
    def __init__(
        self,
        *,
        image: builtins.str,
        container_name: typing.Optional[builtins.str] = None,
        container_port: typing.Optional[jsii.Number] = None,
        family: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image: The image used to start a container.
        :param container_name: The name of the container. Default: ``sample-website``
        :param container_port: Default: 80
        :param family: The name of a family that this task definition is registered to. A family groups multiple versions of a task definition. Default: - Automatically generated name.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "image": image,
        }
        if container_name is not None:
            self._values["container_name"] = container_name
        if container_port is not None:
            self._values["container_port"] = container_port
        if family is not None:
            self._values["family"] = family

    @builtins.property
    def image(self) -> builtins.str:
        '''The image used to start a container.'''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_name(self) -> typing.Optional[builtins.str]:
        '''The name of the container.

        :default: ``sample-website``
        '''
        result = self._values.get("container_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def container_port(self) -> typing.Optional[jsii.Number]:
        '''
        :default: 80
        '''
        result = self._values.get("container_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def family(self) -> typing.Optional[builtins.str]:
        '''The name of a family that this task definition is registered to.

        A family groups multiple versions of a task definition.

        :default: - Automatically generated name.
        '''
        result = self._values.get("family")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DummyTaskDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.EcsDeploymentConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_config_name": "deploymentConfigName",
        "minimum_healthy_hosts": "minimumHealthyHosts",
        "traffic_routing_config": "trafficRoutingConfig",
    },
)
class EcsDeploymentConfigurationProps:
    def __init__(
        self,
        *,
        deployment_config_name: typing.Optional[builtins.str] = None,
        minimum_healthy_hosts: typing.Optional[typing.Union[aws_cdk.aws_codedeploy.CfnDeploymentConfig.MinimumHealthyHostsProperty, aws_cdk.core.IResolvable]] = None,
        traffic_routing_config: typing.Optional[typing.Union[aws_cdk.core.IResolvable, aws_cdk.aws_codedeploy.CfnDeploymentConfig.TrafficRoutingConfigProperty]] = None,
    ) -> None:
        '''
        :param deployment_config_name: ``AWS::CodeDeploy::DeploymentConfig.DeploymentConfigName``.
        :param minimum_healthy_hosts: ``AWS::CodeDeploy::DeploymentConfig.MinimumHealthyHosts``.
        :param traffic_routing_config: ``AWS::CodeDeploy::DeploymentConfig.TrafficRoutingConfig``.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if deployment_config_name is not None:
            self._values["deployment_config_name"] = deployment_config_name
        if minimum_healthy_hosts is not None:
            self._values["minimum_healthy_hosts"] = minimum_healthy_hosts
        if traffic_routing_config is not None:
            self._values["traffic_routing_config"] = traffic_routing_config

    @builtins.property
    def deployment_config_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeDeploy::DeploymentConfig.DeploymentConfigName``.

        :external: true
        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentconfig.html#cfn-codedeploy-deploymentconfig-deploymentconfigname
        '''
        result = self._values.get("deployment_config_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum_healthy_hosts(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.aws_codedeploy.CfnDeploymentConfig.MinimumHealthyHostsProperty, aws_cdk.core.IResolvable]]:
        '''``AWS::CodeDeploy::DeploymentConfig.MinimumHealthyHosts``.

        :external: true
        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentconfig.html#cfn-codedeploy-deploymentconfig-minimumhealthyhosts
        '''
        result = self._values.get("minimum_healthy_hosts")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.aws_codedeploy.CfnDeploymentConfig.MinimumHealthyHostsProperty, aws_cdk.core.IResolvable]], result)

    @builtins.property
    def traffic_routing_config(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, aws_cdk.aws_codedeploy.CfnDeploymentConfig.TrafficRoutingConfigProperty]]:
        '''``AWS::CodeDeploy::DeploymentConfig.TrafficRoutingConfig``.

        :external: true
        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentconfig.html#cfn-codedeploy-deploymentconfig-trafficroutingconfig
        '''
        result = self._values.get("traffic_routing_config")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.core.IResolvable, aws_cdk.aws_codedeploy.CfnDeploymentConfig.TrafficRoutingConfigProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsDeploymentConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.EcsDeploymentGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "deployment_group_name": "deploymentGroupName",
        "ecs_services": "ecsServices",
        "prod_traffic_listener": "prodTrafficListener",
        "target_groups": "targetGroups",
        "test_traffic_listener": "testTrafficListener",
        "application_name": "applicationName",
        "auto_rollback_on_events": "autoRollbackOnEvents",
        "deployment_config": "deploymentConfig",
        "termination_wait_time": "terminationWaitTime",
    },
)
class EcsDeploymentGroupProps:
    def __init__(
        self,
        *,
        deployment_group_name: builtins.str,
        ecs_services: typing.Sequence["IEcsService"],
        prod_traffic_listener: "TrafficListener",
        target_groups: typing.Sequence[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup],
        test_traffic_listener: "TrafficListener",
        application_name: typing.Optional[builtins.str] = None,
        auto_rollback_on_events: typing.Optional[typing.Sequence["RollbackEvent"]] = None,
        deployment_config: typing.Optional["IEcsDeploymentConfig"] = None,
        termination_wait_time: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param deployment_group_name: -
        :param ecs_services: -
        :param prod_traffic_listener: -
        :param target_groups: -
        :param test_traffic_listener: -
        :param application_name: -
        :param auto_rollback_on_events: The event type or types that trigger a rollback.
        :param deployment_config: -
        :param termination_wait_time: the number of minutes before deleting the original (blue) task set. During an Amazon ECS deployment, CodeDeploy shifts traffic from the original (blue) task set to a replacement (green) task set. The maximum setting is 2880 minutes (2 days). Default: 60 minutes
        '''
        if isinstance(prod_traffic_listener, dict):
            prod_traffic_listener = TrafficListener(**prod_traffic_listener)
        if isinstance(test_traffic_listener, dict):
            test_traffic_listener = TrafficListener(**test_traffic_listener)
        self._values: typing.Dict[str, typing.Any] = {
            "deployment_group_name": deployment_group_name,
            "ecs_services": ecs_services,
            "prod_traffic_listener": prod_traffic_listener,
            "target_groups": target_groups,
            "test_traffic_listener": test_traffic_listener,
        }
        if application_name is not None:
            self._values["application_name"] = application_name
        if auto_rollback_on_events is not None:
            self._values["auto_rollback_on_events"] = auto_rollback_on_events
        if deployment_config is not None:
            self._values["deployment_config"] = deployment_config
        if termination_wait_time is not None:
            self._values["termination_wait_time"] = termination_wait_time

    @builtins.property
    def deployment_group_name(self) -> builtins.str:
        result = self._values.get("deployment_group_name")
        assert result is not None, "Required property 'deployment_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ecs_services(self) -> typing.List["IEcsService"]:
        result = self._values.get("ecs_services")
        assert result is not None, "Required property 'ecs_services' is missing"
        return typing.cast(typing.List["IEcsService"], result)

    @builtins.property
    def prod_traffic_listener(self) -> "TrafficListener":
        result = self._values.get("prod_traffic_listener")
        assert result is not None, "Required property 'prod_traffic_listener' is missing"
        return typing.cast("TrafficListener", result)

    @builtins.property
    def target_groups(
        self,
    ) -> typing.List[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup]:
        result = self._values.get("target_groups")
        assert result is not None, "Required property 'target_groups' is missing"
        return typing.cast(typing.List[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup], result)

    @builtins.property
    def test_traffic_listener(self) -> "TrafficListener":
        result = self._values.get("test_traffic_listener")
        assert result is not None, "Required property 'test_traffic_listener' is missing"
        return typing.cast("TrafficListener", result)

    @builtins.property
    def application_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("application_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_rollback_on_events(self) -> typing.Optional[typing.List["RollbackEvent"]]:
        '''The event type or types that trigger a rollback.'''
        result = self._values.get("auto_rollback_on_events")
        return typing.cast(typing.Optional[typing.List["RollbackEvent"]], result)

    @builtins.property
    def deployment_config(self) -> typing.Optional["IEcsDeploymentConfig"]:
        result = self._values.get("deployment_config")
        return typing.cast(typing.Optional["IEcsDeploymentConfig"], result)

    @builtins.property
    def termination_wait_time(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''the number of minutes before deleting the original (blue) task set.

        During an Amazon ECS deployment, CodeDeploy shifts traffic from the
        original (blue) task set to a replacement (green) task set.

        The maximum setting is 2880 minutes (2 days).

        :default: 60 minutes
        '''
        result = self._values.get("termination_wait_time")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsDeploymentGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.EcsServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "prod_target_group": "prodTargetGroup",
        "service_name": "serviceName",
        "task_definition": "taskDefinition",
        "test_target_group": "testTargetGroup",
        "circuit_breaker": "circuitBreaker",
        "container_port": "containerPort",
        "desired_count": "desiredCount",
        "health_check_grace_period": "healthCheckGracePeriod",
        "launch_type": "launchType",
        "max_healthy_percent": "maxHealthyPercent",
        "min_healthy_percent": "minHealthyPercent",
        "platform_version": "platformVersion",
        "propagate_tags": "propagateTags",
        "security_groups": "securityGroups",
    },
)
class EcsServiceProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_ecs.ICluster,
        prod_target_group: aws_cdk.aws_elasticloadbalancingv2.ITargetGroup,
        service_name: builtins.str,
        task_definition: "DummyTaskDefinition",
        test_target_group: aws_cdk.aws_elasticloadbalancingv2.ITargetGroup,
        circuit_breaker: typing.Optional[aws_cdk.aws_ecs.DeploymentCircuitBreaker] = None,
        container_port: typing.Optional[jsii.Number] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        health_check_grace_period: typing.Optional[aws_cdk.core.Duration] = None,
        launch_type: typing.Optional[aws_cdk.aws_ecs.LaunchType] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[builtins.str] = None,
        propagate_tags: typing.Optional["PropagateTags"] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.SecurityGroup]] = None,
    ) -> None:
        '''
        :param cluster: -
        :param prod_target_group: -
        :param service_name: -
        :param task_definition: -
        :param test_target_group: -
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param container_port: -
        :param desired_count: -
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param launch_type: -
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param platform_version: -
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. If no value is specified, the tags aren't propagated. Default: - no propagate
        :param security_groups: -
        '''
        if isinstance(circuit_breaker, dict):
            circuit_breaker = aws_cdk.aws_ecs.DeploymentCircuitBreaker(**circuit_breaker)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "prod_target_group": prod_target_group,
            "service_name": service_name,
            "task_definition": task_definition,
            "test_target_group": test_target_group,
        }
        if circuit_breaker is not None:
            self._values["circuit_breaker"] = circuit_breaker
        if container_port is not None:
            self._values["container_port"] = container_port
        if desired_count is not None:
            self._values["desired_count"] = desired_count
        if health_check_grace_period is not None:
            self._values["health_check_grace_period"] = health_check_grace_period
        if launch_type is not None:
            self._values["launch_type"] = launch_type
        if max_healthy_percent is not None:
            self._values["max_healthy_percent"] = max_healthy_percent
        if min_healthy_percent is not None:
            self._values["min_healthy_percent"] = min_healthy_percent
        if platform_version is not None:
            self._values["platform_version"] = platform_version
        if propagate_tags is not None:
            self._values["propagate_tags"] = propagate_tags
        if security_groups is not None:
            self._values["security_groups"] = security_groups

    @builtins.property
    def cluster(self) -> aws_cdk.aws_ecs.ICluster:
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_ecs.ICluster, result)

    @builtins.property
    def prod_target_group(self) -> aws_cdk.aws_elasticloadbalancingv2.ITargetGroup:
        result = self._values.get("prod_target_group")
        assert result is not None, "Required property 'prod_target_group' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ITargetGroup, result)

    @builtins.property
    def service_name(self) -> builtins.str:
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task_definition(self) -> "DummyTaskDefinition":
        result = self._values.get("task_definition")
        assert result is not None, "Required property 'task_definition' is missing"
        return typing.cast("DummyTaskDefinition", result)

    @builtins.property
    def test_target_group(self) -> aws_cdk.aws_elasticloadbalancingv2.ITargetGroup:
        result = self._values.get("test_target_group")
        assert result is not None, "Required property 'test_target_group' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ITargetGroup, result)

    @builtins.property
    def circuit_breaker(
        self,
    ) -> typing.Optional[aws_cdk.aws_ecs.DeploymentCircuitBreaker]:
        '''Whether to enable the deployment circuit breaker.

        If this property is defined, circuit breaker will be implicitly
        enabled.

        :default: - disabled
        '''
        result = self._values.get("circuit_breaker")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.DeploymentCircuitBreaker], result)

    @builtins.property
    def container_port(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("container_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def desired_count(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("desired_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def health_check_grace_period(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started.

        :default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        '''
        result = self._values.get("health_check_grace_period")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def launch_type(self) -> typing.Optional[aws_cdk.aws_ecs.LaunchType]:
        result = self._values.get("launch_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.LaunchType], result)

    @builtins.property
    def max_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment.

        :default: - 100 if daemon, otherwise 200
        '''
        result = self._values.get("max_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_healthy_percent(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment.

        :default: - 0 if daemon, otherwise 50
        '''
        result = self._values.get("min_healthy_percent")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def platform_version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("platform_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def propagate_tags(self) -> typing.Optional["PropagateTags"]:
        '''Specifies whether to propagate the tags from the task definition or the service to the tasks in the service.

        If no value is specified, the tags aren't propagated.

        :default: - no propagate
        '''
        result = self._values.get("propagate_tags")
        return typing.cast(typing.Optional["PropagateTags"], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.SecurityGroup]]:
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.SecurityGroup]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.IDummyTaskDefinition"
)
class IDummyTaskDefinition(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerPort")
    def container_port(self) -> jsii.Number:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> aws_cdk.aws_iam.IRole:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskDefinitionArn")
    def task_definition_arn(self) -> builtins.str:
        ...


class _IDummyTaskDefinitionProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-blue-green-container-deployment.IDummyTaskDefinition"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerPort")
    def container_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "containerPort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> aws_cdk.aws_iam.IRole:
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "executionRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskDefinitionArn")
    def task_definition_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskDefinitionArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDummyTaskDefinition).__jsii_proxy_class__ = lambda : _IDummyTaskDefinitionProxy


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.IEcsDeploymentConfig"
)
class IEcsDeploymentConfig(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigArn")
    def deployment_config_arn(self) -> builtins.str:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> builtins.str:
        ...


class _IEcsDeploymentConfigProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-blue-green-container-deployment.IEcsDeploymentConfig"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigArn")
    def deployment_config_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentConfigArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentConfigName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEcsDeploymentConfig).__jsii_proxy_class__ = lambda : _IEcsDeploymentConfigProxy


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.IEcsDeploymentGroup"
)
class IEcsDeploymentGroup(aws_cdk.core.IResource, typing_extensions.Protocol):
    '''Interface for an ECS deployment group.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="application")
    def application(self) -> aws_cdk.aws_codedeploy.IEcsApplication:
        '''The reference to the CodeDeploy ECS Application that this Deployment Group belongs to.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfig")
    def deployment_config(self) -> IEcsDeploymentConfig:
        '''The Deployment Configuration this Group uses.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> builtins.str:
        '''The ARN of this Deployment Group.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> builtins.str:
        '''The physical name of the CodeDeploy Deployment Group.'''
        ...


class _IEcsDeploymentGroupProxy(
    jsii.proxy_for(aws_cdk.core.IResource) # type: ignore[misc]
):
    '''Interface for an ECS deployment group.'''

    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-blue-green-container-deployment.IEcsDeploymentGroup"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="application")
    def application(self) -> aws_cdk.aws_codedeploy.IEcsApplication:
        '''The reference to the CodeDeploy ECS Application that this Deployment Group belongs to.'''
        return typing.cast(aws_cdk.aws_codedeploy.IEcsApplication, jsii.get(self, "application"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfig")
    def deployment_config(self) -> IEcsDeploymentConfig:
        '''The Deployment Configuration this Group uses.'''
        return typing.cast(IEcsDeploymentConfig, jsii.get(self, "deploymentConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> builtins.str:
        '''The ARN of this Deployment Group.'''
        return typing.cast(builtins.str, jsii.get(self, "deploymentGroupArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> builtins.str:
        '''The physical name of the CodeDeploy Deployment Group.'''
        return typing.cast(builtins.str, jsii.get(self, "deploymentGroupName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEcsDeploymentGroup).__jsii_proxy_class__ = lambda : _IEcsDeploymentGroupProxy


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.IEcsService"
)
class IEcsService(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        ...


class _IEcsServiceProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-blue-green-container-deployment.IEcsService"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEcsService).__jsii_proxy_class__ = lambda : _IEcsServiceProxy


@jsii.enum(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.PropagateTags"
)
class PropagateTags(enum.Enum):
    TASK_DEFINITION = "TASK_DEFINITION"
    SERVICE = "SERVICE"


class PushImageProject(
    aws_cdk.aws_codebuild.PipelineProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.PushImageProject",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        image_repository: aws_cdk.aws_ecr.IRepository,
        task_definition: IDummyTaskDefinition,
        build_spec: typing.Optional[aws_cdk.aws_codebuild.BuildSpec] = None,
        cache: typing.Optional[aws_cdk.aws_codebuild.Cache] = None,
        compute_type: typing.Optional[aws_cdk.aws_codebuild.ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_codebuild.BuildEnvironmentVariable]] = None,
        project_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param image_repository: -
        :param task_definition: -
        :param build_spec: -
        :param cache: -
        :param compute_type: -
        :param environment_variables: -
        :param project_name: -
        '''
        props = PushImageProjectProps(
            image_repository=image_repository,
            task_definition=task_definition,
            build_spec=build_spec,
            cache=cache,
            compute_type=compute_type,
            environment_variables=environment_variables,
            project_name=project_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.PushImageProjectProps",
    jsii_struct_bases=[],
    name_mapping={
        "image_repository": "imageRepository",
        "task_definition": "taskDefinition",
        "build_spec": "buildSpec",
        "cache": "cache",
        "compute_type": "computeType",
        "environment_variables": "environmentVariables",
        "project_name": "projectName",
    },
)
class PushImageProjectProps:
    def __init__(
        self,
        *,
        image_repository: aws_cdk.aws_ecr.IRepository,
        task_definition: IDummyTaskDefinition,
        build_spec: typing.Optional[aws_cdk.aws_codebuild.BuildSpec] = None,
        cache: typing.Optional[aws_cdk.aws_codebuild.Cache] = None,
        compute_type: typing.Optional[aws_cdk.aws_codebuild.ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_codebuild.BuildEnvironmentVariable]] = None,
        project_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image_repository: -
        :param task_definition: -
        :param build_spec: -
        :param cache: -
        :param compute_type: -
        :param environment_variables: -
        :param project_name: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "image_repository": image_repository,
            "task_definition": task_definition,
        }
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if cache is not None:
            self._values["cache"] = cache
        if compute_type is not None:
            self._values["compute_type"] = compute_type
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if project_name is not None:
            self._values["project_name"] = project_name

    @builtins.property
    def image_repository(self) -> aws_cdk.aws_ecr.IRepository:
        result = self._values.get("image_repository")
        assert result is not None, "Required property 'image_repository' is missing"
        return typing.cast(aws_cdk.aws_ecr.IRepository, result)

    @builtins.property
    def task_definition(self) -> IDummyTaskDefinition:
        result = self._values.get("task_definition")
        assert result is not None, "Required property 'task_definition' is missing"
        return typing.cast(IDummyTaskDefinition, result)

    @builtins.property
    def build_spec(self) -> typing.Optional[aws_cdk.aws_codebuild.BuildSpec]:
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.BuildSpec], result)

    @builtins.property
    def cache(self) -> typing.Optional[aws_cdk.aws_codebuild.Cache]:
        result = self._values.get("cache")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.Cache], result)

    @builtins.property
    def compute_type(self) -> typing.Optional[aws_cdk.aws_codebuild.ComputeType]:
        result = self._values.get("compute_type")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.ComputeType], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_codebuild.BuildEnvironmentVariable]]:
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_codebuild.BuildEnvironmentVariable]], result)

    @builtins.property
    def project_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("project_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PushImageProjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.RollbackEvent"
)
class RollbackEvent(enum.Enum):
    DEPLOYMENT_FAILURE = "DEPLOYMENT_FAILURE"
    DEPLOYMENT_STOP_ON_ALARM = "DEPLOYMENT_STOP_ON_ALARM"
    DEPLOYMENT_STOP_ON_REQUEST = "DEPLOYMENT_STOP_ON_REQUEST"


@jsii.enum(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.SchedulingStrategy"
)
class SchedulingStrategy(enum.Enum):
    REPLICA = "REPLICA"
    DAEMON = "DAEMON"


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.TrafficListener",
    jsii_struct_bases=[],
    name_mapping={"listener_arn": "listenerArn"},
)
class TrafficListener:
    def __init__(self, *, listener_arn: builtins.str) -> None:
        '''
        :param listener_arn: ARN of the listener.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "listener_arn": listener_arn,
        }

    @builtins.property
    def listener_arn(self) -> builtins.str:
        '''ARN of the listener.

        :attribute: true
        '''
        result = self._values.get("listener_arn")
        assert result is not None, "Required property 'listener_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TrafficListener(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IDummyTaskDefinition, aws_cdk.core.ITaggable)
class DummyTaskDefinition(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.DummyTaskDefinition",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        image: builtins.str,
        container_name: typing.Optional[builtins.str] = None,
        container_port: typing.Optional[jsii.Number] = None,
        family: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param image: The image used to start a container.
        :param container_name: The name of the container. Default: ``sample-website``
        :param container_port: Default: 80
        :param family: The name of a family that this task definition is registered to. A family groups multiple versions of a task definition. Default: - Automatically generated name.
        '''
        props = DummyTaskDefinitionProps(
            image=image,
            container_name=container_name,
            container_port=container_port,
            family=family,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addToExecutionRolePolicy")
    def add_to_execution_role_policy(
        self,
        statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> None:
        '''Adds a policy statement to the task execution IAM role.

        :param statement: -
        '''
        return typing.cast(None, jsii.invoke(self, "addToExecutionRolePolicy", [statement]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerPort")
    def container_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "containerPort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> aws_cdk.aws_iam.IRole:
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "executionRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''TagManager to set, remove and format tags.'''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskDefinitionArn")
    def task_definition_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taskDefinitionArn"))


@jsii.implements(IEcsDeploymentConfig)
class EcsDeploymentConfig(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.EcsDeploymentConfig",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        deployment_config_name: typing.Optional[builtins.str] = None,
        minimum_healthy_hosts: typing.Optional[typing.Union[aws_cdk.aws_codedeploy.CfnDeploymentConfig.MinimumHealthyHostsProperty, aws_cdk.core.IResolvable]] = None,
        traffic_routing_config: typing.Optional[typing.Union[aws_cdk.core.IResolvable, aws_cdk.aws_codedeploy.CfnDeploymentConfig.TrafficRoutingConfigProperty]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param deployment_config_name: ``AWS::CodeDeploy::DeploymentConfig.DeploymentConfigName``.
        :param minimum_healthy_hosts: ``AWS::CodeDeploy::DeploymentConfig.MinimumHealthyHosts``.
        :param traffic_routing_config: ``AWS::CodeDeploy::DeploymentConfig.TrafficRoutingConfig``.
        '''
        props = EcsDeploymentConfigurationProps(
            deployment_config_name=deployment_config_name,
            minimum_healthy_hosts=minimum_healthy_hosts,
            traffic_routing_config=traffic_routing_config,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromEcsDeploymentConfigName") # type: ignore[misc]
    @builtins.classmethod
    def from_ecs_deployment_config_name(
        cls,
        _scope: aws_cdk.core.Construct,
        _id: builtins.str,
        ecs_deployment_config_name: builtins.str,
    ) -> IEcsDeploymentConfig:
        '''Import a custom Deployment Configuration for an ECS Deployment Group defined outside the CDK.

        :param _scope: the parent Construct for this new Construct.
        :param _id: the logical ID of this new Construct.
        :param ecs_deployment_config_name: the name of the referenced custom Deployment Configuration.

        :return: a Construct representing a reference to an existing custom Deployment Configuration
        '''
        return typing.cast(IEcsDeploymentConfig, jsii.sinvoke(cls, "fromEcsDeploymentConfigName", [_scope, _id, ecs_deployment_config_name]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ALL_AT_ONCE")
    def ALL_AT_ONCE(cls) -> IEcsDeploymentConfig:
        return typing.cast(IEcsDeploymentConfig, jsii.sget(cls, "ALL_AT_ONCE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CANARY_10PERCENT_15MINUTES")
    def CANARY_10_PERCENT_15_MINUTES(cls) -> IEcsDeploymentConfig:
        return typing.cast(IEcsDeploymentConfig, jsii.sget(cls, "CANARY_10PERCENT_15MINUTES"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CANARY_10PERCENT_5MINUTES")
    def CANARY_10_PERCENT_5_MINUTES(cls) -> IEcsDeploymentConfig:
        return typing.cast(IEcsDeploymentConfig, jsii.sget(cls, "CANARY_10PERCENT_5MINUTES"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LINEAR_10PERCENT_EVERY_1MINUTE")
    def LINEAR_10_PERCENT_EVERY_1_MINUTE(cls) -> IEcsDeploymentConfig:
        return typing.cast(IEcsDeploymentConfig, jsii.sget(cls, "LINEAR_10PERCENT_EVERY_1MINUTE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LINEAR_10PERCENT_EVERY_3MINUTES")
    def LINEAR_10_PERCENT_EVERY_3_MINUTES(cls) -> IEcsDeploymentConfig:
        return typing.cast(IEcsDeploymentConfig, jsii.sget(cls, "LINEAR_10PERCENT_EVERY_3MINUTES"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigArn")
    def deployment_config_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentConfigArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfigName")
    def deployment_config_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentConfigName"))


@jsii.implements(IEcsDeploymentGroup, aws_cdk.core.ITaggable)
class EcsDeploymentGroup(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.EcsDeploymentGroup",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        deployment_group_name: builtins.str,
        ecs_services: typing.Sequence[IEcsService],
        prod_traffic_listener: TrafficListener,
        target_groups: typing.Sequence[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup],
        test_traffic_listener: TrafficListener,
        application_name: typing.Optional[builtins.str] = None,
        auto_rollback_on_events: typing.Optional[typing.Sequence[RollbackEvent]] = None,
        deployment_config: typing.Optional[IEcsDeploymentConfig] = None,
        termination_wait_time: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param deployment_group_name: -
        :param ecs_services: -
        :param prod_traffic_listener: -
        :param target_groups: -
        :param test_traffic_listener: -
        :param application_name: -
        :param auto_rollback_on_events: The event type or types that trigger a rollback.
        :param deployment_config: -
        :param termination_wait_time: the number of minutes before deleting the original (blue) task set. During an Amazon ECS deployment, CodeDeploy shifts traffic from the original (blue) task set to a replacement (green) task set. The maximum setting is 2880 minutes (2 days). Default: 60 minutes
        '''
        props = EcsDeploymentGroupProps(
            deployment_group_name=deployment_group_name,
            ecs_services=ecs_services,
            prod_traffic_listener=prod_traffic_listener,
            target_groups=target_groups,
            test_traffic_listener=test_traffic_listener,
            application_name=application_name,
            auto_rollback_on_events=auto_rollback_on_events,
            deployment_config=deployment_config,
            termination_wait_time=termination_wait_time,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="application")
    def application(self) -> aws_cdk.aws_codedeploy.IEcsApplication:
        '''The reference to the CodeDeploy ECS Application that this Deployment Group belongs to.'''
        return typing.cast(aws_cdk.aws_codedeploy.IEcsApplication, jsii.get(self, "application"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentConfig")
    def deployment_config(self) -> IEcsDeploymentConfig:
        '''The Deployment Configuration this Group uses.'''
        return typing.cast(IEcsDeploymentConfig, jsii.get(self, "deploymentConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> builtins.str:
        '''The ARN of this Deployment Group.'''
        return typing.cast(builtins.str, jsii.get(self, "deploymentGroupArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> builtins.str:
        '''The physical name of the CodeDeploy Deployment Group.'''
        return typing.cast(builtins.str, jsii.get(self, "deploymentGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''TagManager to set, remove and format tags.'''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))


@jsii.implements(aws_cdk.aws_ec2.IConnectable, IEcsService, aws_cdk.core.ITaggable)
class EcsService(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-blue-green-container-deployment.EcsService",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_ecs.ICluster,
        prod_target_group: aws_cdk.aws_elasticloadbalancingv2.ITargetGroup,
        service_name: builtins.str,
        task_definition: DummyTaskDefinition,
        test_target_group: aws_cdk.aws_elasticloadbalancingv2.ITargetGroup,
        circuit_breaker: typing.Optional[aws_cdk.aws_ecs.DeploymentCircuitBreaker] = None,
        container_port: typing.Optional[jsii.Number] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        health_check_grace_period: typing.Optional[aws_cdk.core.Duration] = None,
        launch_type: typing.Optional[aws_cdk.aws_ecs.LaunchType] = None,
        max_healthy_percent: typing.Optional[jsii.Number] = None,
        min_healthy_percent: typing.Optional[jsii.Number] = None,
        platform_version: typing.Optional[builtins.str] = None,
        propagate_tags: typing.Optional[PropagateTags] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.SecurityGroup]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: -
        :param prod_target_group: -
        :param service_name: -
        :param task_definition: -
        :param test_target_group: -
        :param circuit_breaker: Whether to enable the deployment circuit breaker. If this property is defined, circuit breaker will be implicitly enabled. Default: - disabled
        :param container_port: -
        :param desired_count: -
        :param health_check_grace_period: The period of time, in seconds, that the Amazon ECS service scheduler ignores unhealthy Elastic Load Balancing target health checks after a task has first started. Default: - defaults to 60 seconds if at least one load balancer is in-use and it is not already set
        :param launch_type: -
        :param max_healthy_percent: The maximum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that can run in a service during a deployment. Default: - 100 if daemon, otherwise 200
        :param min_healthy_percent: The minimum number of tasks, specified as a percentage of the Amazon ECS service's DesiredCount value, that must continue to run and remain healthy during a deployment. Default: - 0 if daemon, otherwise 50
        :param platform_version: -
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the service to the tasks in the service. If no value is specified, the tags aren't propagated. Default: - no propagate
        :param security_groups: -
        '''
        props = EcsServiceProps(
            cluster=cluster,
            prod_target_group=prod_target_group,
            service_name=service_name,
            task_definition=task_definition,
            test_target_group=test_target_group,
            circuit_breaker=circuit_breaker,
            container_port=container_port,
            desired_count=desired_count,
            health_check_grace_period=health_check_grace_period,
            launch_type=launch_type,
            max_healthy_percent=max_healthy_percent,
            min_healthy_percent=min_healthy_percent,
            platform_version=platform_version,
            propagate_tags=propagate_tags,
            security_groups=security_groups,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''The network connections associated with this resource.'''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''TagManager to set, remove and format tags.'''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))


__all__ = [
    "DummyTaskDefinition",
    "DummyTaskDefinitionProps",
    "EcsDeploymentConfig",
    "EcsDeploymentConfigurationProps",
    "EcsDeploymentGroup",
    "EcsDeploymentGroupProps",
    "EcsService",
    "EcsServiceProps",
    "IDummyTaskDefinition",
    "IEcsDeploymentConfig",
    "IEcsDeploymentGroup",
    "IEcsService",
    "PropagateTags",
    "PushImageProject",
    "PushImageProjectProps",
    "RollbackEvent",
    "SchedulingStrategy",
    "TrafficListener",
]

publication.publish()
