import logging
import re

from ethereum.raw_data.aws_utils import AWSUtil
from ethereum.raw_data.etl_command_wrapper import ETLCommandWrapper
from ethereum.raw_data.resource import Resource


class ResourceStage:
    logger = logging.getLogger(__name__)

    resource_name: str

    workspace_dir: str

    exclude_columns: [int]

    bytea_columns: [int]

    aws_util: AWSUtil

    def __init__(self,
                 resource: Resource,
                 workspace_dir: str,
                 aws_util: AWSUtil):
        self.resource_name = resource.name
        self.workspace_dir = workspace_dir
        self.redshift_table_name = resource.redshift_table_name
        self.exclude_columns = resource.exclude_columns
        self.bytea_columns = resource.bytea_columns
        self.aws_util = aws_util

    def run(self, output_path: str, start_block: int):
        filtrate_output_path = ResourceStage._get_action_output_path(self.workspace_dir,
                                                                     self.resource_name,
                                                                     start_block,
                                                                     'filtrate')
        ETLCommandWrapper.remove_if_exists(filtrate_output_path)
        self._do_filtrate(output_path, filtrate_output_path, self.exclude_columns, self.bytea_columns)

        s3_path = self.aws_util.get_resource_s3_path(self.resource_name, start_block)
        self.aws_util.copy_to_s3(filtrate_output_path, self.aws_util.s3_bucket, s3_path)
        self.aws_util.copy_to_redshift(f'crypto.ethereum.{self.redshift_table_name}',
                                       f's3://{self.aws_util.s3_bucket}/{s3_path}')

        ETLCommandWrapper.remove_if_exists(output_path)
        ETLCommandWrapper.remove_if_exists(filtrate_output_path)
        self.aws_util.rm_s3(self.aws_util.s3_bucket, s3_path)

        self.logger.info(
            f'Finish a resource stage, resource name: {self.resource_name}, start block: {start_block}')

    def _do_filtrate(self,
                     output_path: str,
                     filtrated_output_path: str,
                     exclude_columns: [int],
                     bytea_columns: [int]):
        with open(output_path, "r") as rf:
            with open(filtrated_output_path, "w") as wf:
                while True:
                    try:
                        line = ResourceStage._split_and_standardize(next(rf))
                        selected_items = []
                        for index in range(len(line)):
                            if index not in exclude_columns:
                                content = line[index]
                                if index in bytea_columns:
                                    content = content[2:]
                                selected_items.append(content)
                        wf.write(",".join(selected_items) + "\n")
                    except StopIteration:
                        break

        self.logger.debug(f'Finish filtrate {output_path} to {filtrated_output_path}.')

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
