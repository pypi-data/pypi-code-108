import logging
import re

from ethereum.raw_data.aws_utils import AWSUtil
from ethereum.raw_data.etl_command_wrapper import ETLCommandWrapper
from ethereum.raw_data.resource import Resource


class ResourceStage:
    logger = logging.getLogger(__name__)

    resource_name: str

    workspace_dir: str

    aws_util: AWSUtil

    def __init__(self,
                 resource: Resource,
                 workspace_dir: str,
                 aws_util: AWSUtil):
        self.resource_name = resource.name
        self.workspace_dir = workspace_dir
        self.redshift_table_name = resource.redshift_table_name
        self.aws_util = aws_util

    def run(self, output_path: str, start_block: int):
        s3_path = self.aws_util.get_resource_s3_path(self.resource_name, start_block)
        self.aws_util.copy_to_s3(output_path, self.aws_util.s3_bucket, s3_path)
        self.aws_util.copy_to_redshift(f'crypto.ethereum.{self.redshift_table_name}',
                                       f's3://{self.aws_util.s3_bucket}/{s3_path}')

        ETLCommandWrapper.remove_if_exists(output_path)
        self.aws_util.rm_s3(self.aws_util.s3_bucket, s3_path)

        self.logger.info(
            f'Finish a resource stage, resource name: {self.resource_name}, start block: {start_block}')

    @staticmethod
    def _get_action_output_path(workspace_dir: str,
                                resource_name: str,
                                started_at: int,
                                action: str) -> str:
        return f'{workspace_dir}/{resource_name}_{started_at}_{action}.csv'

    @staticmethod
    def _split_and_standardize(line_str: str) -> [str]:
        COMMA_MATCHER = re.compile(r",(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)")
        return [item.replace('\n', '') for item in COMMA_MATCHER.split(line_str)]
