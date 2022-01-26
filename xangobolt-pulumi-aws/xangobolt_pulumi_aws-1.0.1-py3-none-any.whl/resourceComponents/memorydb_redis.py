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

from resources import memorydb, ec2


class MemoryDB4Redis(ComponentResource):
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

        Resources = [memorydb]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags

        # Get needed stack exports
        vpcid = stackref.get_output('vpc_'+props.stack)
        snet1 = stackref.get_output('snet1_'+props.stack)
        snet2 = stackref.get_output('snet2_'+props.stack)
        snet3 = stackref.get_output('snet3_'+props.stack)


        # Create Redis Cluster
        redis_cluster = [memorydb.Cluster(
            props.mdb[i]["cluster_name"],
            props,
            acl_name=(memorydb.Acl(
                props.mdb[i]["acl"]["acl_name"],
                props,
                usernames=[(memorydb.User(
                    props.mdb[i]["acl"]["user"]["username"],
                    props,
                    username=props.mdb[i]["acl"]["user"]["username"],
                    passwords=props.mdb[i]["acl"]["user"]["passwords"],
                    accessstring=props.mdb[i]["acl"]["user"]["access_string"],
                    parent=self, 
                    provider=opts.providers.get(props.stack+'_prov')))
                ],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov'))
            .id),
            secgrp_ids=[(ec2.SecurityGroup(
                props.mdb[i]["setflow_sg"]["sg_name"],
                props,
                vpc_id=vpcid, 
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).id)
            ],
            snetgrp_name=(memorydb.SubnetGroup(
                props.mdb[i]["snetgrp_name"],
                props,
                snet_ids=[snet1,snet2,snet3],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).name),
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.mdb
        ]




        