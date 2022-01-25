import json
import logging
import os.path
from typing import Dict

from ethereum.raw_data.aws_utils import AWSUtil
from ethereum.raw_data.job.base_job import BaseJob
from ethereum.raw_data.resource import resource_map
from ethereum.raw_data.resource_stage import ResourceStage


def init_aws_util(workspace_dir: str) -> AWSUtil:
    aws_conf = f'{workspace_dir}/aws_conf.json'
    assert os.path.isfile(aws_conf)

    with open(aws_conf, 'r') as f:
        content = f.read()
        assert len(content) > 0
        content_dict = json.loads(content)
        redshift_dict = content_dict['redshift']
        s3_dict = content_dict['s3']

        return AWSUtil(
            redshift_host=redshift_dict['host'],
            redshift_port=int(redshift_dict['port']),
            redshift_database=redshift_dict['database'],
            redshift_user=redshift_dict['user'],
            redshift_password=redshift_dict['password'],
            s3_bucket=s3_dict['bucket']
        )


class ExtractJob(BaseJob):
    logger = logging.getLogger(__name__)

    stage_map: Dict[str, ResourceStage]

    step_size: int

    uri: str

    batch_size: int

    max_workers: int

    def __init__(self,
                 resources: [str],
                 step_size: int,
                 job_name: str,
                 start_block: int,
                 end_block: int,
                 workspace_dir: str,
                 uri: str,
                 batch_size: int,
                 max_workers: int):
        super().__init__(job_name, start_block, end_block, workspace_dir)

        aws_util = init_aws_util(workspace_dir)
        resource_objs = [resource_map[resource] for resource in resources]

        self.stage_map = {resource.name: ResourceStage(
            resource=resource,
            workspace_dir=workspace_dir,
            aws_util=aws_util
        ) for resource in resource_objs}

        self.step_size = step_size
        self.uri = uri
        self.batch_size = batch_size
        self.max_workers = max_workers

    def extract_output(self, _end_block: int) -> Dict[str, str]:
        pass

    def run(self):
        start = self.start_block

        while start < self.end_block:
            next_start = min(start + self.step_size, self.end_block)
            progress = format((start - self.start_block_custom) / (self.end_block - self.start_block_custom) * 100,
                              '.2f')

            self.logger.info(
                f'>>>>>>>>>> Start to get {start} to {next_start} blocks, progress: {progress}% <<<<<<<<<<')

            output_map = self.extract_output(next_start)

            for resource in output_map:
                self.stage_map[resource].run(output_path=output_map[resource], start_block=start)

            start = next_start
            self.save_next_start(start)
