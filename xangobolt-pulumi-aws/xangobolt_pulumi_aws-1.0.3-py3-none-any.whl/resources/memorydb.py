from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.memorydb as memdb
import pulumi_aws_native.memorydb as memdb_native
from resources.ec2 import SecurityGroup

def Cluster(stem, props, acl_name=None, secgrp_ids=None, snetgrp_name=None, provider=None, parent=None, depends_on=None):
    db_cluster =memdb.Cluster(
        f'memdb-{stem}',
        name=f'memdb-{stem}',
        acl_name="open-access",
        node_type="db.t4g.small",
        num_shards=1,
        num_replicas_per_shard=1,
        snapshot_retention_limit=1,
        tls_enabled='false',
        security_group_ids=secgrp_ids,
        subnet_group_name=snetgrp_name,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return db_cluster

def SubnetGroup(stem, props, snet_ids=None, provider=None, parent=None, depends_on=None):
    sn_grp =memdb.SubnetGroup(
        f'sngrp-{stem}',
        name=f'sngrp-{stem}',
        subnet_ids=snet_ids,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sn_grp

def Acl(stem, props, usernames=None, provider=None, parent=None, depends_on=None):
    sn_grp =memdb.Acl(
        f'mdbacl-{stem}',
        name=f'mdbacl-{stem}',
        user_names=usernames,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sn_grp

def User(stem, props, username=None, passwords=None, accessstring=None, provider=None, parent=None, depends_on=None):
    sn_grp =memdb.User(
        f'mdbuser-{stem}',
        user_name=username,
        authentication_mode=memdb.UserAuthenticationModeArgs(
            passwords=passwords,
            type="password",
        ),
        access_string=accessstring,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sn_grp

