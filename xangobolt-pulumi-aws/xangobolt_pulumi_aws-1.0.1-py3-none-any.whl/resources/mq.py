from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.mq as mq
# import pulumi_aws_native.mq as mq

def Broker(stem, props, db_name=None, username=None, password=None, secgrp_ids=None, snet_ids=None, provider=None, parent=None, depends_on=None):
    rs_cluster = mq.Broker(
        f'mq-{stem}',
        broker_name=f'mq-{stem}',
        users=[mq.BrokerUserArgs(
            username=username,
            password=password,
        )],
        engine_type="RabbitMQ",
        engine_version="3.8.23",
        deployment_mode="CLUSTER_MULTI_AZ",
        host_instance_type="mq.t3.micro",
        security_groups=secgrp_ids,
        subnet_ids=snet_ids,
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return rs_cluster