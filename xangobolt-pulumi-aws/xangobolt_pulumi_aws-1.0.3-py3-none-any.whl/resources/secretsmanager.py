from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.secretsmanager as sm
import pulumi_aws_native.secretsmanager as sm_native

def Secret(stem, props, provider=None, parent=None, depends_on=None):
    sm_secret = sm.Secret(
        f'secman-{stem}',
        bucket=f's3-{stem}',
        acl='private',
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return sm_secret