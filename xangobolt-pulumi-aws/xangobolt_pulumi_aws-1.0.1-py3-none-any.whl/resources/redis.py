from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.memorydb as memdb
import pulumi_aws_native.memorydb as memdb_native

def Cluster(stem, props, provider=None, parent=None, depends_on=None):
    db_cluster =memdb.Cluster(
        f'memdb-{stem}',
        name=f'memdb-{stem}',
        acl_name="open-access",
        node_type="db.t4g.small",
        num_shards=1,
        num_replicas_per_shard=2,
        snapshot_retention_limit=1,
        security_group_ids=[aws_security_group["example"]["id"]],
        subnet_group_name=aws_memorydb_subnet_group["example"]["id"],
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return db_cluster