'''
# aws-alb-fargate module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_alb_fargate`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-alb-fargate`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.albfargate`|

This AWS Solutions Construct implements an an Application Load Balancer to an AWS Fargate service

Here is a minimal deployable pattern definition in Typescript:

```python
  import { AlbToFargate, AlbToFargateProps } from '@aws-solutions-constructs/aws-alb-fargate';

  // Obtain a pre-existing certificate from your account
  const certificate = acm.Certificate.fromCertificateArn(
        scope,
        'existing-cert',
        "arn:aws:acm:us-east-1:123456789012:certificate/11112222-3333-1234-1234-123456789012"
      );

  const props: AlbToFargateProps = {
    ecrRepositoryArn: "arn:aws:ecr:us-east-1:123456789012:repository/your-ecr-repo",
    ecrImageVersion: "latest",
    listenerProps: {
      certificates: [ certificate ]
    },
    publicApi: true
  };

  new AlbToFargate(stack, 'new-construct', props);
```

## Initializer

```text
new AlbToFargate(scope: Construct, id: string, props: AlbToFargateProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`AlbToFargateProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| publicApi | boolean | Whether the construct is deploying a private or public API. This has implications for the VPC and ALB. |
| loadBalancerProps? | [elasticloadbalancingv2.ApplicationLoadBalancerProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancerProps.html) | Optional custom properties for a new loadBalancer. Providing both this and existingLoadBalancer is an error. This cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. |
| existingLoadBalancerObj? | [elasticloadbalancingv2.ApplicationLoadBalancer](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancer.html) | [existing Application Load Balancer to incorporate into the construct architecture. Providing both this and loadBalancerProps is an error. The VPC containing this loadBalancer must match the VPC provided in existingVpc.|
| listenerProps? | [ApplicationListenerProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationListenerProps.html) | Props to define the listener. Must be provided when adding the listener to an ALB (eg - when creating the alb), may not be provided when adding a second target to an already established listener. When provided, must include either a certificate or protocol: HTTP |
| targetGroupProps? | [ApplicationTargetGroupProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationTargetGroupProps.html) | Optional custom properties for a new target group. If your application requires end to end encryption, then you should set the protocol attribute to [elb.ApplicationProtocol.HTTPS](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationProtocol.html) and use a container that can accept HTTPS traffic. |
| ruleProps? | [AddRuleProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.AddRuleProps.html) | Rules for directing traffic to the target being created. Must not be specified for the first listener added to an ALB, and must be specified for the second target added to a listener. Add a second target by instantiating this construct a second time and providing the existingAlb from the first instantiation. |
| vpcProps? | [ec2.VpcProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.VpcProps.html) | Optional custom properties for a VPC the construct will create. This VPC will be used by the new ALB and any Private Hosted Zone the construct creates (that's why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing both this and existingVpc is an error. |
| existingVpc? | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing load balancer and/or existing Private Hosted Zone, those constructs must exist in this VPC. |
| logAlbAccessLogs? | boolean| Whether to turn on Access Logs for the Application Load Balancer. Uses an S3 bucket with associated storage costs.Enabling Access Logging is a best practice. default - true |
| albLoggingBucketProps? | [s3.BucketProps](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html) | Optional properties to customize the bucket used to store the ALB Access Logs. Supplying this and setting logAccessLogs to false is an error. @default - none |
| clusterProps? | [ecs.ClusterProps](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.ClusterProps.html) | Optional properties to create a new ECS cluster. To provide an existing cluster, use the cluster attribute of fargateServiceProps. |
| ecrRepositoryArn? | string | The arn of an ECR Repository containing the image to use to generate the containers. Either this or the image property of containerDefinitionProps must be provided. format: arn:aws:ecr:*region*:*account number*:repository/*Repository Name* |
| ecrImageVersion? | string | The version of the image to use from the repository. Defaults to 'Latest' |
| containerDefinitionProps? | [ecs.ContainerDefinitionProps | any](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.ContainerDefinitionProps.html) | Optional props to define the container created for the Fargate Service (defaults found in fargate-defaults.ts) |
| fargateTaskDefinitionProps? | [ecs.FargateTaskDefinitionProps | any](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateTaskDefinitionProps.html) | Optional props to define the Fargate Task Definition for this construct  (defaults found in fargate-defaults.ts) |
| fargateServiceProps? | [ecs.FargateServiceProps | any](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateServiceProps.html) | Optional properties to override default values for the Fargate service. Service will set up in the Public or Isolated subnets of the VPC by default, override that (e.g. - choose Private subnets) by setting vpcSubnets on this object. |
| existingFargateServiceObject? | [ecs.FargateService](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateService.html) | A Fargate Service already instantiated (probably by another Solutions Construct). If this is specified, then no props defining a new service can be provided, including: existingImageObject, ecrImageVersion, containerDefintionProps, fargateTaskDefinitionProps, ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface |
| existingContainerDefinitionObject? | [ecs.ContainerDefinition](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.ContainerDefinition.html) | A container definition already instantiated as part of a Fargate service. This must be the container in the existingFargateServiceObject |

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
| vpc | [ec2.IVpc](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.IVpc.html) | The VPC used by the construct (whether created by the construct or providedb by the client) |
| loadBalancer | [elasticloadbalancingv2.ApplicationLoadBalancer](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationLoadBalancer.html) | The Load Balancer used by the construct (whether created by the construct or provided by the client) |
| listener | [elb.ApplicationListener](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-elasticloadbalancingv2.ApplicationListener.html) | The listener used by this pattern. |
| service | [ecs.FargateService](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.FargateService.html) | The AWS Fargate service used by this construct (whether created by this construct or passed to this construct at initialization) |
| container | [ecs.ContainerDefinition](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-ecs.ContainerDefinition.html) | The container associated with the AWS Fargate service in the service property. |

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Application Load Balancer

* Creates or configures an Application Load Balancer with:

  * Required listeners
  * New target group with routing rules if appropriate

### AWS Fargate Service

* Sets up an AWS Fargate service as a target of the Application Load Balancer

  * Uses the existing service if provided
  * Creates a new service if none provided.

    * Service will run in isolated subnets if available, then private subnets if available and finally public subnets

## Architecture

![Architecture Diagram](architecture.png)

---


© Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_s3
import aws_cdk.core


class AlbToFargate(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-alb-fargate.AlbToFargate",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        public_api: builtins.bool,
        alb_logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        cluster_props: typing.Optional[aws_cdk.aws_ecs.ClusterProps] = None,
        container_definition_props: typing.Any = None,
        ecr_image_version: typing.Optional[builtins.str] = None,
        ecr_repository_arn: typing.Optional[builtins.str] = None,
        existing_container_definition_object: typing.Optional[aws_cdk.aws_ecs.ContainerDefinition] = None,
        existing_fargate_service_object: typing.Optional[aws_cdk.aws_ecs.FargateService] = None,
        existing_load_balancer_obj: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        fargate_service_props: typing.Any = None,
        fargate_task_definition_props: typing.Any = None,
        listener_props: typing.Any = None,
        load_balancer_props: typing.Any = None,
        log_alb_access_logs: typing.Optional[builtins.bool] = None,
        rule_props: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.AddRuleProps] = None,
        target_group_props: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param public_api: Whether the construct is deploying a private or public API. This has implications for the VPC and ALB. Default: - none
        :param alb_logging_bucket_props: Optional properties to customize the bucket used to store the ALB Access Logs. Supplying this and setting logAccessLogs to false is an error. Default: - none
        :param cluster_props: Optional properties to create a new ECS cluster.
        :param container_definition_props: Optional props to define the container created for the Fargate Service. Default: - see fargate-defaults.t
        :param ecr_image_version: The version of the image to use from the repository. Default: - none
        :param ecr_repository_arn: The arn of an ECR Repository containing the image to use to generate the containers. format: arn:aws:ecr:[region]:[account number]:repository/[Repository Name]
        :param existing_container_definition_object: The container associated with the service supplied in existingFargateServiceObject. This and existingFargateServiceObject must either both be provided or neither. Default: - none
        :param existing_fargate_service_object: A Fargate Service already instantiated (probably by another Solutions Construct). If this is specified, then no props defining a new service can be provided, including: ecrImageVersion, containerDefintionProps, fargateTaskDefinitionProps, ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface Default: - none
        :param existing_load_balancer_obj: Existing Application Load Balancer to incorporate into the construct architecture. Providing both this and loadBalancerProps is an error. The VPC containing this loadBalancer must match the VPC provided in existingVpc. Default: - none
        :param existing_vpc: An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing load balancer and/or existing Private Hosted Zone, those constructs must exist in this VPC. Default: - none
        :param fargate_service_props: Optional properties to override default values for the Fargate service. Service will set up in the Public or Isolated subnets of the VPC by default, override that (e.g. - choose Private subnets) by setting vpcSubnets on this object. Default: - see core/lib/fargate-defaults.ts
        :param fargate_task_definition_props: Optional props to define the Fargate Task Definition for this construct. Default: - see fargate-defaults.ts
        :param listener_props: Props to define the listener. Must be provided when adding the listener to an ALB (eg - when creating the alb), may not be provided when adding a second target to an already established listener. When provided, must include either a certificate or protocol: HTTP Default: - none
        :param load_balancer_props: Optional custom properties for a new loadBalancer. Providing both this and existingLoadBalancer is an error. This cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. Default: - none
        :param log_alb_access_logs: Whether to turn on Access Logs for the Application Load Balancer. Uses an S3 bucket with associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param rule_props: Rules for directing traffic to the target being created. May not be specified for the first listener added to an ALB, and must be specified for the second target added to a listener. Add a second target by instantiating this construct a second time and providing the existingAlb from the first instantiation. Default: - none
        :param target_group_props: Optional custom properties for a new target group. While this is a standard attribute of props for ALB constructs, there are few pertinent properties for a Lambda target. Default: - none
        :param vpc_props: Optional custom properties for a VPC the construct will create. This VPC will be used by the new ALB and any Private Hosted Zone the construct creates (that's why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing both this and existingVpc is an error. Default: - none
        '''
        props = AlbToFargateProps(
            public_api=public_api,
            alb_logging_bucket_props=alb_logging_bucket_props,
            cluster_props=cluster_props,
            container_definition_props=container_definition_props,
            ecr_image_version=ecr_image_version,
            ecr_repository_arn=ecr_repository_arn,
            existing_container_definition_object=existing_container_definition_object,
            existing_fargate_service_object=existing_fargate_service_object,
            existing_load_balancer_obj=existing_load_balancer_obj,
            existing_vpc=existing_vpc,
            fargate_service_props=fargate_service_props,
            fargate_task_definition_props=fargate_task_definition_props,
            listener_props=listener_props,
            load_balancer_props=load_balancer_props,
            log_alb_access_logs=log_alb_access_logs,
            rule_props=rule_props,
            target_group_props=target_group_props,
            vpc_props=vpc_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="container")
    def container(self) -> aws_cdk.aws_ecs.ContainerDefinition:
        return typing.cast(aws_cdk.aws_ecs.ContainerDefinition, jsii.get(self, "container"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="listener")
    def listener(self) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationListener:
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationListener, jsii.get(self, "listener"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadBalancer")
    def load_balancer(
        self,
    ) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer:
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, jsii.get(self, "loadBalancer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> aws_cdk.aws_ecs.FargateService:
        return typing.cast(aws_cdk.aws_ecs.FargateService, jsii.get(self, "service"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-alb-fargate.AlbToFargateProps",
    jsii_struct_bases=[],
    name_mapping={
        "public_api": "publicApi",
        "alb_logging_bucket_props": "albLoggingBucketProps",
        "cluster_props": "clusterProps",
        "container_definition_props": "containerDefinitionProps",
        "ecr_image_version": "ecrImageVersion",
        "ecr_repository_arn": "ecrRepositoryArn",
        "existing_container_definition_object": "existingContainerDefinitionObject",
        "existing_fargate_service_object": "existingFargateServiceObject",
        "existing_load_balancer_obj": "existingLoadBalancerObj",
        "existing_vpc": "existingVpc",
        "fargate_service_props": "fargateServiceProps",
        "fargate_task_definition_props": "fargateTaskDefinitionProps",
        "listener_props": "listenerProps",
        "load_balancer_props": "loadBalancerProps",
        "log_alb_access_logs": "logAlbAccessLogs",
        "rule_props": "ruleProps",
        "target_group_props": "targetGroupProps",
        "vpc_props": "vpcProps",
    },
)
class AlbToFargateProps:
    def __init__(
        self,
        *,
        public_api: builtins.bool,
        alb_logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        cluster_props: typing.Optional[aws_cdk.aws_ecs.ClusterProps] = None,
        container_definition_props: typing.Any = None,
        ecr_image_version: typing.Optional[builtins.str] = None,
        ecr_repository_arn: typing.Optional[builtins.str] = None,
        existing_container_definition_object: typing.Optional[aws_cdk.aws_ecs.ContainerDefinition] = None,
        existing_fargate_service_object: typing.Optional[aws_cdk.aws_ecs.FargateService] = None,
        existing_load_balancer_obj: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer] = None,
        existing_vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        fargate_service_props: typing.Any = None,
        fargate_task_definition_props: typing.Any = None,
        listener_props: typing.Any = None,
        load_balancer_props: typing.Any = None,
        log_alb_access_logs: typing.Optional[builtins.bool] = None,
        rule_props: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.AddRuleProps] = None,
        target_group_props: typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps] = None,
        vpc_props: typing.Optional[aws_cdk.aws_ec2.VpcProps] = None,
    ) -> None:
        '''
        :param public_api: Whether the construct is deploying a private or public API. This has implications for the VPC and ALB. Default: - none
        :param alb_logging_bucket_props: Optional properties to customize the bucket used to store the ALB Access Logs. Supplying this and setting logAccessLogs to false is an error. Default: - none
        :param cluster_props: Optional properties to create a new ECS cluster.
        :param container_definition_props: Optional props to define the container created for the Fargate Service. Default: - see fargate-defaults.t
        :param ecr_image_version: The version of the image to use from the repository. Default: - none
        :param ecr_repository_arn: The arn of an ECR Repository containing the image to use to generate the containers. format: arn:aws:ecr:[region]:[account number]:repository/[Repository Name]
        :param existing_container_definition_object: The container associated with the service supplied in existingFargateServiceObject. This and existingFargateServiceObject must either both be provided or neither. Default: - none
        :param existing_fargate_service_object: A Fargate Service already instantiated (probably by another Solutions Construct). If this is specified, then no props defining a new service can be provided, including: ecrImageVersion, containerDefintionProps, fargateTaskDefinitionProps, ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface Default: - none
        :param existing_load_balancer_obj: Existing Application Load Balancer to incorporate into the construct architecture. Providing both this and loadBalancerProps is an error. The VPC containing this loadBalancer must match the VPC provided in existingVpc. Default: - none
        :param existing_vpc: An existing VPC in which to deploy the construct. Providing both this and vpcProps is an error. If the client provides an existing load balancer and/or existing Private Hosted Zone, those constructs must exist in this VPC. Default: - none
        :param fargate_service_props: Optional properties to override default values for the Fargate service. Service will set up in the Public or Isolated subnets of the VPC by default, override that (e.g. - choose Private subnets) by setting vpcSubnets on this object. Default: - see core/lib/fargate-defaults.ts
        :param fargate_task_definition_props: Optional props to define the Fargate Task Definition for this construct. Default: - see fargate-defaults.ts
        :param listener_props: Props to define the listener. Must be provided when adding the listener to an ALB (eg - when creating the alb), may not be provided when adding a second target to an already established listener. When provided, must include either a certificate or protocol: HTTP Default: - none
        :param load_balancer_props: Optional custom properties for a new loadBalancer. Providing both this and existingLoadBalancer is an error. This cannot specify a VPC, it will use the VPC in existingVpc or the VPC created by the construct. Default: - none
        :param log_alb_access_logs: Whether to turn on Access Logs for the Application Load Balancer. Uses an S3 bucket with associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param rule_props: Rules for directing traffic to the target being created. May not be specified for the first listener added to an ALB, and must be specified for the second target added to a listener. Add a second target by instantiating this construct a second time and providing the existingAlb from the first instantiation. Default: - none
        :param target_group_props: Optional custom properties for a new target group. While this is a standard attribute of props for ALB constructs, there are few pertinent properties for a Lambda target. Default: - none
        :param vpc_props: Optional custom properties for a VPC the construct will create. This VPC will be used by the new ALB and any Private Hosted Zone the construct creates (that's why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing both this and existingVpc is an error. Default: - none
        '''
        if isinstance(alb_logging_bucket_props, dict):
            alb_logging_bucket_props = aws_cdk.aws_s3.BucketProps(**alb_logging_bucket_props)
        if isinstance(cluster_props, dict):
            cluster_props = aws_cdk.aws_ecs.ClusterProps(**cluster_props)
        if isinstance(rule_props, dict):
            rule_props = aws_cdk.aws_elasticloadbalancingv2.AddRuleProps(**rule_props)
        if isinstance(target_group_props, dict):
            target_group_props = aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps(**target_group_props)
        if isinstance(vpc_props, dict):
            vpc_props = aws_cdk.aws_ec2.VpcProps(**vpc_props)
        self._values: typing.Dict[str, typing.Any] = {
            "public_api": public_api,
        }
        if alb_logging_bucket_props is not None:
            self._values["alb_logging_bucket_props"] = alb_logging_bucket_props
        if cluster_props is not None:
            self._values["cluster_props"] = cluster_props
        if container_definition_props is not None:
            self._values["container_definition_props"] = container_definition_props
        if ecr_image_version is not None:
            self._values["ecr_image_version"] = ecr_image_version
        if ecr_repository_arn is not None:
            self._values["ecr_repository_arn"] = ecr_repository_arn
        if existing_container_definition_object is not None:
            self._values["existing_container_definition_object"] = existing_container_definition_object
        if existing_fargate_service_object is not None:
            self._values["existing_fargate_service_object"] = existing_fargate_service_object
        if existing_load_balancer_obj is not None:
            self._values["existing_load_balancer_obj"] = existing_load_balancer_obj
        if existing_vpc is not None:
            self._values["existing_vpc"] = existing_vpc
        if fargate_service_props is not None:
            self._values["fargate_service_props"] = fargate_service_props
        if fargate_task_definition_props is not None:
            self._values["fargate_task_definition_props"] = fargate_task_definition_props
        if listener_props is not None:
            self._values["listener_props"] = listener_props
        if load_balancer_props is not None:
            self._values["load_balancer_props"] = load_balancer_props
        if log_alb_access_logs is not None:
            self._values["log_alb_access_logs"] = log_alb_access_logs
        if rule_props is not None:
            self._values["rule_props"] = rule_props
        if target_group_props is not None:
            self._values["target_group_props"] = target_group_props
        if vpc_props is not None:
            self._values["vpc_props"] = vpc_props

    @builtins.property
    def public_api(self) -> builtins.bool:
        '''Whether the construct is deploying a private or public API.

        This has implications for the VPC and ALB.

        :default: - none
        '''
        result = self._values.get("public_api")
        assert result is not None, "Required property 'public_api' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def alb_logging_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Optional properties to customize the bucket used to store the ALB Access Logs.

        Supplying this and setting logAccessLogs to false is an error.

        :default: - none
        '''
        result = self._values.get("alb_logging_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def cluster_props(self) -> typing.Optional[aws_cdk.aws_ecs.ClusterProps]:
        '''Optional properties to create a new ECS cluster.'''
        result = self._values.get("cluster_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ClusterProps], result)

    @builtins.property
    def container_definition_props(self) -> typing.Any:
        '''Optional props to define the container created for the Fargate Service.

        :default: - see fargate-defaults.t
        '''
        result = self._values.get("container_definition_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def ecr_image_version(self) -> typing.Optional[builtins.str]:
        '''The version of the image to use from the repository.

        :default: - none
        '''
        result = self._values.get("ecr_image_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecr_repository_arn(self) -> typing.Optional[builtins.str]:
        '''The arn of an ECR Repository containing the image to use to generate the containers.

        format:
        arn:aws:ecr:[region]:[account number]:repository/[Repository Name]
        '''
        result = self._values.get("ecr_repository_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def existing_container_definition_object(
        self,
    ) -> typing.Optional[aws_cdk.aws_ecs.ContainerDefinition]:
        '''The container associated with the service supplied in existingFargateServiceObject.

        This and existingFargateServiceObject must either both be provided or neither.

        :default: - none
        '''
        result = self._values.get("existing_container_definition_object")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ContainerDefinition], result)

    @builtins.property
    def existing_fargate_service_object(
        self,
    ) -> typing.Optional[aws_cdk.aws_ecs.FargateService]:
        '''A Fargate Service already instantiated (probably by another Solutions Construct).

        If
        this is specified, then no props defining a new service can be provided, including:
        ecrImageVersion, containerDefintionProps, fargateTaskDefinitionProps,
        ecrRepositoryArn, fargateServiceProps, clusterProps, existingClusterInterface

        :default: - none
        '''
        result = self._values.get("existing_fargate_service_object")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.FargateService], result)

    @builtins.property
    def existing_load_balancer_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer]:
        '''Existing Application Load Balancer to incorporate into the construct architecture.

        Providing both this and loadBalancerProps is an
        error. The VPC containing this loadBalancer must match the VPC provided in existingVpc.

        :default: - none
        '''
        result = self._values.get("existing_load_balancer_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer], result)

    @builtins.property
    def existing_vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''An existing VPC in which to deploy the construct.

        Providing both this and
        vpcProps is an error. If the client provides an existing load balancer and/or
        existing Private Hosted Zone, those constructs must exist in this VPC.

        :default: - none
        '''
        result = self._values.get("existing_vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def fargate_service_props(self) -> typing.Any:
        '''Optional properties to override default values for the Fargate service.

        Service will set up in the Public or Isolated subnets of the VPC by default,
        override that (e.g. - choose Private subnets) by setting vpcSubnets on this
        object.

        :default: - see core/lib/fargate-defaults.ts
        '''
        result = self._values.get("fargate_service_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def fargate_task_definition_props(self) -> typing.Any:
        '''Optional props to define the Fargate Task Definition for this construct.

        :default: - see fargate-defaults.ts
        '''
        result = self._values.get("fargate_task_definition_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def listener_props(self) -> typing.Any:
        '''Props to define the listener.

        Must be provided when adding the listener
        to an ALB (eg - when creating the alb), may not be provided when adding
        a second target to an already established listener. When provided, must include
        either a certificate or protocol: HTTP

        :default: - none
        '''
        result = self._values.get("listener_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def load_balancer_props(self) -> typing.Any:
        '''Optional custom properties for a new loadBalancer.

        Providing both this and
        existingLoadBalancer is an error. This cannot specify a VPC, it will use the VPC
        in existingVpc or the VPC created by the construct.

        :default: - none
        '''
        result = self._values.get("load_balancer_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def log_alb_access_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether to turn on Access Logs for the Application Load Balancer.

        Uses an S3 bucket
        with associated storage costs. Enabling Access Logging is a best practice.

        :default: - true
        '''
        result = self._values.get("log_alb_access_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def rule_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.AddRuleProps]:
        '''Rules for directing traffic to the target being created.

        May not be specified
        for the first listener added to an ALB, and must be specified for the second
        target added to a listener. Add a second target by instantiating this construct a
        second time and providing the existingAlb from the first instantiation.

        :default: - none
        '''
        result = self._values.get("rule_props")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.AddRuleProps], result)

    @builtins.property
    def target_group_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps]:
        '''Optional custom properties for a new target group.

        While this is a standard
        attribute of props for ALB constructs, there are few pertinent properties for a Lambda target.

        :default: - none
        '''
        result = self._values.get("target_group_props")
        return typing.cast(typing.Optional[aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroupProps], result)

    @builtins.property
    def vpc_props(self) -> typing.Optional[aws_cdk.aws_ec2.VpcProps]:
        '''Optional custom properties for a VPC the construct will create.

        This VPC will
        be used by the new ALB and any Private Hosted Zone the construct creates (that's
        why loadBalancerProps and privateHostedZoneProps can't include a VPC). Providing
        both this and existingVpc is an error.

        :default: - none
        '''
        result = self._values.get("vpc_props")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.VpcProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlbToFargateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AlbToFargate",
    "AlbToFargateProps",
]

publication.publish()
