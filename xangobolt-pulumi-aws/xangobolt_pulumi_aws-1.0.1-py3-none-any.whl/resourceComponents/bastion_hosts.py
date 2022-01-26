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

from resources import ec2


class BastionHosts(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, stackref: None, opts:  ResourceOptions = None):
        """
        Constructs an Rediss Cluster.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('MemoryDB', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [ec2]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags

        # Get needed stack exports
        vpcid = stackref.get_output('vpc_'+props.stack)
        snet1 = stackref.get_output('snet1_'+props.stack)
        snet2 = stackref.get_output('snet2_'+props.stack)
        snet3 = stackref.get_output('snet3_'+props.stack)


        # Create Bastion Hosts
        ec2_BASTION = [ec2.Instance(
            props.bh[i]["instance_name"],
            props,
            lt_id=(ec2.LaunchTemplates(
                props.bh[i]["instance_name"],
                props,
                sg_ids=[(ec2.SecurityGroup(
                    props.bh[i]["bh_lt"]["lt_sg"]['sg_name'],
                    props,
                    vpc_id=vpcid, 
                    parent=self, 
                    provider=opts.providers.get(props.stack+'_prov')).id)
                ],
                vpc_id=vpcid, 
                snet_ids=[snet1,snet2,snet3], 
                #iam_ip_arn="arn:aws:iam::554290308952:instance-profile/EC2AppAccess
                iam_ip_arn="arn:aws:iam::917340184633:instance-profile/EC2AppAccess",
                image_id=props.bh[i]["bh_lt"]["image_id"],
                instance_type=props.bh[i]["bh_lt"]["instance_type"],
                key_name=props.bh[i]["bh_lt"]["key_pair"],
                user_data=props.bh[i]["bh_lt"]["user_data"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).id),
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.bh
        ]




        