from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_aws.kms as kms
import pulumi_aws_native.kms as kms_native

def KMS_Key(stem, props, ku=None, ekr=None , dwid=None, cmks=None, desc=None, provider=None, parent=None, depends_on=None):
    kms_key = kms.Key(
        f'kms-{stem}',
        bypass_policy_lockout_safety_check='false',
        customer_master_key_spec=cmks or 'SYMMETRIC_DEFAULT',
        deletion_window_in_days=dwid or 7,
        description=desc or "",
        enable_key_rotation=ekr or 'false',
        key_usage=ku or 'ENCRYPT_DECRYPT',
        tags=props.base_tags,
        opts=ResourceOptions(provider=provider, parent=parent, depends_on=depends_on)
    )
    return kms_key