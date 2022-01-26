import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from djaws import decorators as aws_decorators
from djaws.cloudformation.exceptions import CFError
from djaws.utils import ClientErrorResponse

from djstarter import utils as dj_utils


def cf_session_client(*args, **kwargs):
    session = boto3.session.Session()
    return session.client(
        'cloudformation',
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        *args,
        **kwargs
    )


@aws_decorators.wrap_and_reraise_cloudformation_errors
def describe_stacks(cf_client, stack_name):
    try:
        r_stacks = cf_client.describe_stacks(StackName=stack_name)
    except ClientError as e:
        raise CFClientErrorResponse(e.response).to_cf_exception
    else:
        return DescribeStacksResponse(r_stacks)


class DescribeStacksResponse(dj_utils.SerializerMixin):
    class Stack:
        def __init__(self, data):
            self.stack_id = data.get('StackId')
            self.stack_name = data.get('StackName')
            self.description = data.get('Description')
            self.creation_time = data.get('CreationTime')
            self.stack_status = data.get('StackStatus')

    def __init__(self, data):
        self.stacks = [self.Stack(s) for s in data.get('Stacks', list())]

    @property
    def first_stack(self):
        return self.stacks[0]


class CFClientErrorResponse(ClientErrorResponse):
    EXC_MAP = dict()

    @property
    def to_cf_exception(self):
        return self.EXC_MAP.get(self.exception_class, CFError)(self.__dict__)
