# Copyright 2018-2019, James Nugent.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain
# one at http://mozilla.org/MPL/2.0/.

"""
Contains a Pulumi ComponentResource for creating a good-practice AWS VPC.
"""
import json, pulumi
from typing import Mapping, Sequence
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi import Input
# from pulumi_aws import cloudwatch, config, ec2, iam

from resources import ec2

# from .iam_helpers import assume_role_policy_for_principal
from .subnet_distributor import SubnetDistributor



class VirtualPrivateCloud(ComponentResource):
    """
    Creates a good-practice AWS VPC using Pulumi. The VPC consists of:

      - DHCP options for the given private hosted zone name
      - An Internet gateway
      - Subnets of appropriate sizes for public and private subnets, for each availability zone specified
      - A route table routing traffic from public subnets to the internet gateway
      - NAT gateways (and accoutrements) for each private subnet, and appropriate routing
      - Optionally, S3 and DynamoDB endpoints
    """

    def __init__(self, name: str, props: None, opts:  ResourceOptions = None):
        """
        Constructs a Vpc.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        :param args: A VpcArgs object containing the arguments for VPC constructin.
        :param opts: A pulumi.ResourceOptions object.
        """
        super().__init__('Vpc', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [ec2]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags

        # Create VPC and Internet Gateway resources
        hubvpc = ec2.vpc_classic(name,
            props,
            provider=opts.providers.get(props.stack+'_prov'),
            parent=self,
            depends_on=self
        )

        internet_gateway = ec2.internet_gateway(name,
            vpc_Id=hubvpc.id,
            props=props,
            depends_on=hubvpc,
            parent=hubvpc,
            provider=opts.providers.get(props.stack+'_prov')
        )

        # # Calculate subnet CIDR blocks and create subnets
        subnet_distributor = SubnetDistributor(props, props.base_cidr, len(props.availability_zone_names))

        public_subnets = [ec2.subnet(f"{name}-public-subnet-{i}",
            props=props,
            vpc_Id=hubvpc.id,
            cidr_block=cidr,
            az=props.availability_zone_names[i],
            public=True,
            parent=hubvpc,
            provider=opts.providers.get(props.stack+'_prov')
        )
            for i, cidr in enumerate(subnet_distributor.public_subnets)]

        private_subnets = [ec2.subnet(f"{name}-private-subnet-{i}",
            props=props, 
            vpc_Id=hubvpc.id,
            cidr_block=cidr,
            az=props.availability_zone_names[i],
            public=False,
            parent=hubvpc,
            provider=opts.providers.get(props.stack+'_prov'),
        )
            for i, cidr in enumerate(subnet_distributor.private_subnets)]

    # Adopt the default route table for this VPC and adapt it for use with public subnets
        public_route_table = ec2.DefaultRouteTable(f"{name}-public-rt",
            props,
            default_route_table_id=hubvpc.default_route_table_id,
            parent=hubvpc,
            provider=opts.providers.get(props.stack+'_prov')
        )

        route_to_internet = ec2.Route(f"{name}-route-public-sn-to-ig",
            props,
            route_table_id=public_route_table.id,
            destination_cidr="0.0.0.0/0",
            gateway_id=internet_gateway.id,
            parent=hubvpc,
            provider=opts.providers.get(props.stack+'_prov')
        )

        for i, subnet in enumerate(public_subnets):
            ec2.RouteTableAssociation(f"{name}-public-rta-{i + 1}",
            props=props,
            subnet_id=subnet.id,
            route_table_id=public_route_table,
            parent=hubvpc,
            provider=opts.providers.get(props.stack+'_prov')
        )

        # self.nat_elastic_ip_addresses: [ec2.Eip] = list()
        # self.nat_gateways: [ec2.NatGateway] = list()
        # self.private_route_tables: [ec2.RouteTable] = list()

    #     # Create a NAT Gateway and appropriate route table for each private subnet
    #     for i, subnet in enumerate(self.private_subnets):
    #         self.nat_elastic_ip_addresses.append(ec2.Eip(f"{name}-nat-{i + 1}",
    #                                                      tags={**args.base_tags,
    #                                                            "Name": f"{args.description} NAT Gateway EIP {i + 1}"},
    #                                                      opts=pulumi.ResourceOptions(
    #                                                          parent=subnet
    #                                                      )))

    #         self.nat_gateways.append(ec2.NatGateway(f"{name}-nat-gateway-{i + 1}",
    #                                                 allocation_id=self.nat_elastic_ip_addresses[i].id,
    #                                                 subnet_id=self.public_subnets[i].id,
    #                                                 tags={**args.base_tags,
    #                                                       "Name": f"{args.description} NAT Gateway {i + 1}"},
    #                                                 opts=pulumi.ResourceOptions(
    #                                                     parent=subnet
    #                                                 )))

    #         self.private_route_tables.append(ec2.RouteTable(f"{name}-private-rt-{i + 1}",
    #                                                         vpc_id=self.vpc.id,
    #                                                         tags={**args.base_tags,
    #                                                               "Name": f"{args.description} Private RT {i + 1}"},
    #                                                         opts=pulumi.ResourceOptions(
    #                                                             parent=subnet
    #                                                         )))

    #         ec2.Route(f"{name}-route-private-sn-to-nat-{i + 1}",
    #                   route_table_id=self.private_route_tables[i].id,
    #                   destination_cidr_block="0.0.0.0/0",
    #                   nat_gateway_id=self.nat_gateways[i].id,
    #                   opts=pulumi.ResourceOptions(
    #                       parent=self.private_route_tables[i]
    #                   ))

    #         ec2.RouteTableAssociation(f"{name}-private-rta-{i + 1}",
    #                                   subnet_id=subnet.id,
    #                                   route_table_id=self.private_route_tables[i].id,
    #                                   opts=pulumi.ResourceOptions(
    #                                       parent=self.private_route_tables[i]
    #                                   ))

    #     # Create S3 endpoint if necessary
    #     if args.create_s3_endpoint:
    #         ec2.VpcEndpoint(f"{name}-s3-endpoint",
    #                         vpc_id=self.vpc.id,
    #                         service_name=f"com.amazonaws.{config.region}.s3",
    #                         route_table_ids=[self.public_route_table.id,
    #                                          *[rt.id for rt in self.private_route_tables]],
    #                         opts=pulumi.ResourceOptions(
    #                             parent=self.vpc
    #                         ))

    #     # Create DynamoDB endpoint if necessary
    #     if args.create_dynamodb_endpoint:
    #         ec2.VpcEndpoint(f"{name}-dynamodb-endpoint",
    #                         vpc_id=self.vpc.id,
    #                         service_name=f"com.amazonaws.{config.region}.dynamodb",
    #                         route_table_ids=[self.public_route_table.id,
    #                                          *[rt.id for rt in self.private_route_tables]],
    #                         opts=pulumi.ResourceOptions(
    #                             parent=self.vpc
    #                         ))

    #     super().register_outputs({})

    # def enableFlowLoggingToS3(self, bucketArn: Input[str], trafficType: Input[str]):
    #     """
    #     Enable VPC flow logging to S3, for the specified traffic type
    #     :param self: VPC instance
    #     :param bucketArn: The arn of the s3 bucket to send logs to
    #     :param trafficType: The traffic type to log: "ALL", "ACCEPT" or "REJECT"
    #     :return: None
    #     """
    #     ec2.FlowLog(f"{self.name}-flow-logs",
    #                 log_destination=bucketArn,
    #                 log_destination_type="s3",
    #                 vpc_id=self.vpc.id,
    #                 traffic_type=trafficType,
    #                 opts=pulumi.ResourceOptions(
    #                    parent=self.vpc,
    #                 ))

    # def enableFlowLoggingToCloudWatchLogs(self, trafficType: Input[str]):
    #     """
    #     Enable VPC flow logging to CloudWatch Logs, for the specified traffic type
    #     :param self: VPC instance
    #     :param trafficType: The traffic type to log: "ALL", "ACCEPT" or "REJECT"
    #     :return: None
    #     """
    #     self.flow_logs_role = iam.Role(f"{self.name}-flow-logs-role",
    #                                    tags={**self.base_tags,
    #                                          "Name": f"{self.description} VPC Flow Logs"},
    #                                    assume_role_policy=assume_role_policy_for_principal({
    #                                        "Service": "vpc-flow-logs.amazonaws.com",
    #                                    }),
    #                                    opts=pulumi.ResourceOptions(
    #                                        parent=self.vpc,
    #                                    ))

    #     self.flow_logs_group = cloudwatch.LogGroup(f"{self.name}-vpc-flow-logs",
    #                                                tags={**self.base_tags,
    #                                                      "Name": f"{self.description} VPC Flow Logs"},
    #                                                opts=pulumi.ResourceOptions(
    #                                                    parent=self.vpc,
    #                                                ))

    #     iam.RolePolicy(f"{self.name}-flow-log-policy",
    #                    name="vpc-flow-logs",
    #                    role=self.flow_logs_role.id,
    #                    policy=json.dumps({
    #                        "Version": "2012-10-17",
    #                        "Statement": [
    #                            {
    #                                "Effect": "Allow",
    #                                "Resource": "*",
    #                                "Action": [
    #                                    "logs:CreateLogGroup",
    #                                    "logs:CreateLogStream",
    #                                    "logs:PutLogEvents",
    #                                    "logs:DescribeLogGroups",
    #                                    "logs:DescribeLogStreams",
    #                                ]
    #                            }
    #                        ]
    #                    }),
    #                    opts=pulumi.ResourceOptions(
    #                        parent=self.flow_logs_role
    #                    ))

    #     ec2.FlowLog(f"{self.name}-flow-logs",
    #                 log_destination=self.flow_logs_group.arn,
    #                 iam_role_arn=self.flow_logs_role.arn,
    #                 vpc_id=self.vpc.id,
    #                 traffic_type=trafficType,
    #                 opts=pulumi.ResourceOptions(
    #                     parent=self.flow_logs_role
    #                 ))


        pulumi.export('vpc_'+props.stack, hubvpc.id)
        pulumi.export('snet1_'+props.stack, public_subnets[0].id)
        pulumi.export('snet2_'+props.stack, public_subnets[1].id)
        pulumi.export('snet3_'+props.stack, public_subnets[2].id)