from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.s3 as s3
import pulumi_aws_native.s3 as s3_native

def S3_Bucket(stem, props, provider=None, parent=None, depends_on=None):
    s3_bucket = s3.Bucket(
        f's3-{stem}',
        bucket=f's3-{stem}',
        acl='private',
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return s3_bucket