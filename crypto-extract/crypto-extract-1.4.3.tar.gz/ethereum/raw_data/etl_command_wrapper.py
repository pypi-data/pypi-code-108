import os
import subprocess
from typing import Dict


class ETLCommandWrapper:

    @staticmethod
    def export_block_and_transaction(start_block: int,
                                     end_block: int,
                                     workspace: str,
                                     uri: str,
                                     batch_size: int,
                                     max_workers: int,
                                     process_map: Dict[int, subprocess.Popen]) -> (str, str):
        block_output_path = ETLCommandWrapper.get_output_path(workspace, "block", start_block)
        transaction_output_path = ETLCommandWrapper.get_output_path(workspace, "transaction", start_block)
        ETLCommandWrapper.remove_if_exists(block_output_path)
        ETLCommandWrapper.remove_if_exists(transaction_output_path)

        ETLCommandWrapper.exec_command(f'ethereumetl export_blocks_and_transactions '
                                       f'--start-block {start_block} '
                                       f'--end-block {end_block} '
                                       f'--provider-uri {uri} '
                                       f'--blocks-output {block_output_path} '
                                       f'--batch-size {batch_size} '
                                       f'--max-workers {max_workers} '
                                       f'--transactions-output {transaction_output_path}', process_map)

        return block_output_path, transaction_output_path

    @staticmethod
    def export_trace(start_block: int,
                     end_block: int,
                     workspace: str,
                     uri: str,
                     batch_size: int,
                     max_workers: int,
                     process_map: Dict[int, subprocess.Popen]) -> str:
        trace_output_path = ETLCommandWrapper.get_output_path(workspace, "trace", start_block)
        ETLCommandWrapper.remove_if_exists(trace_output_path)

        ETLCommandWrapper.exec_command(f'ethereumetl export_traces '
                                       f'--start-block {start_block} '
                                       f'--end-block {end_block} '
                                       f'--provider-uri {uri} '
                                       f'--batch-size {batch_size} '
                                       f'--max-workers {max_workers} '
                                       f'--output {trace_output_path}', process_map)
        return trace_output_path

    @staticmethod
    def export_receipt_and_logs(transaction_output_path: str,
                                start_block: int,
                                workspace: str,
                                uri: str,
                                batch_size: int,
                                max_workers: int,
                                process_map: Dict[int, subprocess.Popen]) -> (str, str, str):
        receipt_output_path = ETLCommandWrapper.get_output_path(workspace, "receipt", start_block)
        log_output_path = ETLCommandWrapper.get_output_path(workspace, "log", start_block)
        transaction_hashes_path = f'{workspace}/transaction_hashes_{start_block}.txt'

        ETLCommandWrapper.remove_if_exists(receipt_output_path)
        ETLCommandWrapper.remove_if_exists(log_output_path)
        ETLCommandWrapper.remove_if_exists(transaction_hashes_path)

        ETLCommandWrapper.exec_command(f'ethereumetl extract_csv_column '
                                       f'--input {transaction_output_path} '
                                       f'--column hash '
                                       f'--prefix 0x '
                                       f'--output {transaction_hashes_path}', process_map)

        ETLCommandWrapper.exec_command(f'ethereumetl export_receipts_and_logs '
                                       f'--transaction-hashes {transaction_hashes_path} '
                                       f'--provider-uri {uri} '
                                       f'--batch-size {batch_size} '
                                       f'--max-workers {max_workers} '
                                       f'--receipts-output {receipt_output_path} '
                                       f'--logs-output {log_output_path}', process_map)

        ETLCommandWrapper.remove_if_exists(transaction_hashes_path)
        return receipt_output_path, log_output_path

    @staticmethod
    def export_contracts(receipt_output_path: str,
                         start_block: int,
                         workspace: str,
                         uri: str,
                         batch_size: int,
                         max_workers: int,
                         process_map: Dict[int, subprocess.Popen]) -> (str, str):
        contract_output_path = ETLCommandWrapper.get_output_path(workspace, "contract", start_block)
        contract_addresses_output_path = f'{workspace}/contract_addresses_{start_block}.txt'

        ETLCommandWrapper.remove_if_exists(contract_output_path)
        ETLCommandWrapper.remove_if_exists(contract_addresses_output_path)

        ETLCommandWrapper.exec_command(f'ethereumetl extract_csv_column '
                                       f'--input {receipt_output_path} '
                                       f'--column contract_address '
                                       f'--prefix 0x '
                                       f'--output {contract_addresses_output_path}', process_map)

        ETLCommandWrapper.exec_command(f'ethereumetl export_contracts '
                                       f'--contract-addresses {contract_addresses_output_path} '
                                       f'--provider-uri {uri} '
                                       f'--batch-size {batch_size} '
                                       f'--max-workers {max_workers} '
                                       f'--output {contract_output_path}', process_map)

        ETLCommandWrapper.remove_if_exists(contract_addresses_output_path)

        return contract_output_path

    @staticmethod
    def get_output_path(workspace_dir: str, resource_name: str, start_at: int) -> str:
        return f'{workspace_dir}/{resource_name}_{start_at}.csv'

    @staticmethod
    def remove_if_exists(path: str):
        if os.path.isfile(path):
            os.remove(path)

    @staticmethod
    def exec_command(command: str, process_map: Dict[int, subprocess.Popen]):
        p = subprocess.Popen(command, shell=True)
        process_map[p.pid] = p
        return_code = p.wait()
        process_map.pop(p.pid)
        assert (return_code == 0)
