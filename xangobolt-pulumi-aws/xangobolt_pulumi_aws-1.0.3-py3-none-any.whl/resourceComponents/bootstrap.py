from pulumi import ComponentResource, ResourceOptions, StackReference
import pulumi, pulumi_aws, pulumi_aws_native
# from ..resources import s3,kms
from resources import s3,kms
from pulumi import Output

class Bootstrap(ComponentResource):
    def __init__(self, name: str, props: None, opts:  ResourceOptions = None):
        super().__init__('Bootstrap', name, {}, opts)

        # Create s3 for backend state management
        backend_s3 = s3.S3_Bucket(
            'pulumi-state-'+props.stack,
            props, 
            parent=self,
            provider=opts.providers.get(props.stack+'_prov')
        )

        # Create KMS key for backend state and secret encryption
        backend_s3 = kms.KMS_Key(
            'pulumi-key-'+props.stack,
            props, 
            parent=self,
            provider=opts.providers.get(props.stack+'_prov')
        )
