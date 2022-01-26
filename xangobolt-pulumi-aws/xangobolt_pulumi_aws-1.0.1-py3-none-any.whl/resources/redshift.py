from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.redshift as redshift
import pulumi_aws_native.redshift as redshift_native

def Cluster(stem, props, db_name=None, username=None, password=None, secgrp_ids=None, snetgrp_name=None, provider=None, parent=None, depends_on=None):
    rs_cluster = redshift.Cluster(
        f'redshift-{stem}',
        cluster_identifier=f'redshift-{stem}',
        database_name=db_name,
        cluster_type="multi-node",
        node_type="dc2.large",
        number_of_nodes=1,
        master_username=username,
        master_password=password,
        cluster_subnet_group_name=snetgrp_name,
        vpc_security_group_ids=secgrp_ids,
        iam_roles=["arn:aws:iam::917340184633:role/RedShiftS3"],
        skip_final_snapshot="True",
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return rs_cluster


def SubnetGroup(stem, props, snet_ids=None, provider=None, parent=None, depends_on=None):
    sn_grp =redshift.SubnetGroup(
        f'sngrp-{stem}',
        name=f'sngrp-{stem}',
        subnet_ids=snet_ids,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sn_grp