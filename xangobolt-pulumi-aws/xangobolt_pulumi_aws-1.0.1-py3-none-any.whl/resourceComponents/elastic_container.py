# Copyright 2018-2019, James Nugent.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain
# one at http://mozilla.org/MPL/2.0/.

"""
Contains a Pulumi ComponentResource for creating a good-practice AWS VPC.
"""
import json, time
from typing import Mapping, Sequence
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi import Input
from pulumi_aws.ecs import task_definition
# from pulumi_aws import cloudwatch, config, ec2, iam

from resources import ecs, s3, lb, ec2, autoscaling
from resourceComponents import load_balancer

# from .iam_helpers import assume_role_policy_for_principal
from .subnet_distributor import SubnetDistributor



class ElasticContainerService(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, stackref: None, opts:  ResourceOptions = None):
        """
        Constructs an ECS Cluster.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('Ecs', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [ecs]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags

        # Get needed stack exports
        vpcid = stackref.get_output('vpc_'+props.stack)
        snet1 = stackref.get_output('snet1_'+props.stack)
        snet2 = stackref.get_output('snet2_'+props.stack)
        snet3 = stackref.get_output('snet3_'+props.stack)


        # Create ECS Security Group
        


        # Create Auto Scaling Group
        ecs_autoscalinggroup = [autoscaling.AutoScaleingGroup(
            props.ecs[i]["capacity_provider"]["autoscaling"]["asg_name"],
            props,
            lt_id=(ec2.LaunchTemplates(
                props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["lt_name"],
                props,
                sg_ids=[(ec2.SecurityGroup(
                    props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]['lt_sg']['sg_name'],
                    props,
                    vpc_id=vpcid, 
                    parent=self, 
                    provider=opts.providers.get(props.stack+'_prov')).id)
                ],
                vpc_id=vpcid, 
                snet_ids=[snet1,snet2,snet3], 
                #iam_ip_arn="arn:aws:iam::554290308952:instance-profile/EC2AppAccess
                iam_ip_arn="arn:aws:iam::917340184633:instance-profile/EC2AppAccess",
                image_id=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["image_id"],
                instance_type=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["instance_type"],
                key_name=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["key_pair"],
                user_data=props.ecs[i]["capacity_provider"]["autoscaling"]["asg_lt"]["user_data"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).id),
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.ecs
        ]

        # Create ECS Cluster
        ecs_cluster = [ecs.ecs_cluster(
            props.ecs[i]["cluster_name"],
            props,
            cp=(ecs.ecs_capacity_provider(
                props.ecs[i]["capacity_provider"]["cp_name"],
                props, 
                asg_arn=ecs_autoscalinggroup[0].arn,
                parent=self,
                depends_on=ecs_autoscalinggroup,
                provider=opts.providers.get(props.stack+'_prov')).name),
            # cp=ecs_capacity_provider[0].name,
            parent=self,
            depends_on=ecs_autoscalinggroup,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.ecs
        ]


        # Create Service
        es = [ecs.ecs_service(
            props.service_def[i]["service_name"], 
            props,
            td_arn=(ecs.ecs_task_definition(
                props.service_def[i]['taskDefinition']["td_name"], 
                props,
                family=props.service_def[i]['taskDefinition']["family_name"],
                volume=props.service_def[i]['taskDefinition']["volume_name"],
                cd=json.dumps(props.service_def[i]['taskDefinition']["container_def"]["container_definitions"]),
                parent=self,
                depends_on=ecs_cluster,
                provider=opts.providers.get(props.stack+'_prov')).arn),
            cluster_id=ecs_cluster[0],
            vpc_id=vpcid,
            tg_id=(load_balancer.ECS_LB(
                props.service_def[i]['targetGroup']["tg_name"], 
                props, 
                snet_ids=[snet1,snet2,snet3],
                vpc_id=vpcid,
                asg_name=ecs_autoscalinggroup[0].name,
                hcp=props.service_def[i]['targetGroup']["healthcheckpath"],
                parent=self,
                depends_on=ecs_cluster,
                provider=opts.providers.get(props.stack+'_prov')).id),
            cp_name=ecs_cluster[0].capacity_providers[0],
            container=props.service_def[i]['taskDefinition']["container_def"]["container_definitions"][0]["name"],
            parent=self,
            depends_on=ecs_cluster,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.service_def
        ]