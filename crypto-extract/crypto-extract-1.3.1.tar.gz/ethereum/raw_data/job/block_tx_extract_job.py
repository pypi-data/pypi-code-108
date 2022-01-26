from typing import Dict

from ethereum.raw_data.etl_command_wrapper import ETLCommandWrapper
from ethereum.raw_data.job.extract_job import ExtractJob


class BlockTXExtractJob(ExtractJob):
    def __init__(self,
                 resources: [str],
                 step_size: int,
                 job_name: str,
                 start_block: int,
                 end_block: int,
                 workspace_dir: str,
                 uri: str,
                 batch_size: int,
                 max_workers: int,
                 receipt_log_batch_size: int,
                 receipt_log_max_workers: int):
        super().__init__(resources,
                         step_size,
                         job_name,
                         start_block,
                         end_block,
                         workspace_dir,
                         uri,
                         batch_size,
                         max_workers)

        self.receipt_log_batch_size = receipt_log_batch_size
        self.receipt_log_max_workers = receipt_log_max_workers

    def extract_output(self, _start_block, _end_block: int) -> Dict[str, str]:
        block_output_path, transaction_output_path = ETLCommandWrapper.export_block_and_transaction(
            start_block=_start_block,
            end_block=_end_block,
            workspace=self.workspace_dir,
            uri=self.uri,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            process_map=self.process_map
        )

        receipt_output_path, log_output_path = ETLCommandWrapper.export_receipt_and_logs(
            transaction_output_path=transaction_output_path,
            start_block=_start_block,
            workspace=self.workspace_dir,
            uri=self.uri,
            batch_size=self.receipt_log_batch_size,
            max_workers=self.receipt_log_max_workers,
            process_map=self.process_map
        )

        contract_output_path = ETLCommandWrapper.export_contracts(
            receipt_output_path=receipt_output_path,
            start_block=_start_block,
            workspace=self.workspace_dir,
            uri=self.uri,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            process_map=self.process_map
        )

        return {
            'block': block_output_path,
            'transaction': transaction_output_path,
            'contract': contract_output_path,
            'receipt': receipt_output_path,
            'log': log_output_path
        }
