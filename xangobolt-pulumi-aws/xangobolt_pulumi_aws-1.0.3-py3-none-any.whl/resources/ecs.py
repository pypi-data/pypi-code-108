from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ProviderResource, ResourceOptions
from pulumi_aws_native.ecs import capacity_provider
from resources import autoscaling, lb
import pulumi_aws.ecs as ecs_classic
import pulumi_aws_native.ecs as ecs_native
import json
# import pulumi.awsx

def ecs_cluster(stem, props, cp, provider=None, parent=None, depends_on=None):
    ec = ecs_classic.Cluster(
        f'ecsCluster-{stem}',
        name=f'ecsCluster-{stem}',
        capacity_providers=[cp],
        settings=[ecs_classic.ClusterSettingArgs(
            name='containerInsights',
            value="enabled",
        )],
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return ec


def ecs_cluster_native(stem, props, provider=None, parent=None, depends_on=None):
    ec = ecs_native.Cluster(
        f'ecs_cluster_native-{stem}',
        cluster_name=f'ecs_cluster_native-{stem}',
        cluster_settings=[ecs_native.ClusterClusterSettingsArgs(
            name='containerInsights',
            value="enabled",
        )],
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return ec


def ecs_capacity_provider(stem, props, sg_ids=None, asg_arn=None, vpc_id=None, provider=None, parent=None, depends_on=None):
    # asg = autoscaling.AutoScaleingGroup(stem, props, provider=provider)
    ecp = ecs_classic.CapacityProvider(
        f'ecp-{stem}',
        name=f'ecp-{stem}',
        auto_scaling_group_provider=ecs_classic.CapacityProviderAutoScalingGroupProviderArgs(
            auto_scaling_group_arn=asg_arn, #or (autoscaling.AutoScaleingGroup(stem, props, sg_ids=sg_ids, vpc_id=vpc_id, provider=provider, parent=parent, depends_on=depends_on).arn),
            managed_scaling=ecs_classic.CapacityProviderAutoScalingGroupProviderManagedScalingArgs(
                maximum_scaling_step_size=3,
                minimum_scaling_step_size=1,
                status="ENABLED",
                target_capacity=100,
            ), 
            # managed_termination_protection="ENABLED"
        ),
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return ecp

def ecs_task_definition(stem, props, cd=None, family=None, volume=None, provider=None, parent=None, depends_on=None):
    # asg = autoscaling.AutoScaleingGroup(stem, props, provider=provider)
    etd = ecs_classic.TaskDefinition(
        f'etd-{stem}',
        family=family,
        container_definitions=cd,
        volumes=[ecs_classic.TaskDefinitionVolumeArgs(
            name=volume,
            docker_volume_configuration=ecs_classic.TaskDefinitionVolumeDockerVolumeConfigurationArgs(
                scope="task",
                # autoprovision=True,
                driver="local",
            ),
        )],
        # placement_constraints=[ecs_classic.TaskDefinitionPlacementConstraintArgs(
        #     type="memberOf",
        #     expression="attribute:ecs.availability-zone in [us-west-2a, us-west-2b]",
        # )],
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on))
    return etd


def ecs_service(stem, props, lb_id=None, td_arn=None, cluster_id=None, tg_id=None, vpc_id=None, cp_name=None, snet_ids=None, container=None, provider=None, parent=None, depends_on=None):
    es = ecs_classic.Service(
        f'service-{stem}',
        cluster=cluster_id,
        task_definition=td_arn,
        desired_count=1,
        capacity_provider_strategies=[ecs_classic.ServiceCapacityProviderStrategyArgs(
            capacity_provider=cp_name,
            # base=3,
            weight=1
        )],
        health_check_grace_period_seconds=120,
        # iam_role=aws_iam_role["foo"]["arn"],
        # ordered_placement_strategies=[ecs_classic.ServiceOrderedPlacementStrategyArgs(
        #     type="binpack",
        #     field="cpu",
        # )],
        # placement_constraints=[ecs_classic.ServicePlacementConstraintArgs(
        #     type="memberOf",
        #     expression="attribute:ecs.availability-zone in [us-west-2a, us-west-2b]",
        # )],
        load_balancers=[ecs_classic.ServiceLoadBalancerArgs(
            # elb_name=lb_id or lb.AppLoadBalancer(stem, props, snet_ids=snet_ids, provider=provider, parent=parent, depends_on=depends_on),
            target_group_arn=tg_id or lb.TargetGroup(stem, props, vpc_id=vpc_id, provider=provider, parent=parent, depends_on=depends_on),
            container_name=container,
            container_port=80,
        )],
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on))
    return es
