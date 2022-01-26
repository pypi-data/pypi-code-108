from typing import Dict

from ethereum.raw_data.etl_command_wrapper import ETLCommandWrapper
from ethereum.raw_data.job.extract_job import ExtractJob


class TraceExtractJob(ExtractJob):
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
        super().__init__(resources,
                         step_size,
                         job_name,
                         start_block,
                         end_block,
                         workspace_dir,
                         uri,
                         batch_size,
                         max_workers)

    def extract_output(self, _start_block: int, _end_block: int) -> Dict[str, str]:
        trace_output_path = ETLCommandWrapper.export_trace(
            start_block=_start_block,
            end_block=_end_block,
            workspace=self.workspace_dir,
            uri=self.uri,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            process_map=self.process_map
        )

        return {
            'trace': trace_output_path
        }
