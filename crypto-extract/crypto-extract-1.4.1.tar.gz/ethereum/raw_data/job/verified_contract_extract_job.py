import csv
import json
import logging
from typing import Dict, Optional

import requests
from lxml import etree

from ethereum.raw_data.etl_command_wrapper import ETLCommandWrapper
from ethereum.raw_data.job.extract_job import ExtractJob, init_aws_util


class VerifiedContractExtractJob(ExtractJob):
    logger = logging.getLogger(__name__)

    def __init__(self,
                 resources: [str],
                 step_size: int,
                 job_name: str,
                 start_block: int,
                 end_block: int,
                 workspace_dir: str,
                 cookie: str,
                 api_key: str):
        super().__init__(resources,
                         step_size,
                         job_name,
                         start_block,
                         end_block,
                         workspace_dir)

        self.cookie = cookie
        self.api_key = api_key
        self.aws_util = init_aws_util(workspace_dir)

    def extract_output(self, _start_block, _end_block: int) -> Dict[str, str]:
        verified_contract_output_path = ETLCommandWrapper.get_output_path(self.workspace_dir,
                                                                          "verified_contract",
                                                                          self.start_block)

        ETLCommandWrapper.remove_if_exists(verified_contract_output_path)

        addresses = self.aws_util.exec_query_get_result(f"""
                    select distinct(contract_address) from ethereum.receipts 
                    where length(contract_address)>0 
                    and block_number<{self.end_block}
                    and block_number>={self.start_block}
                """)

        addresses = set(t[0] for t in addresses)
        self.logger.info(f'Get {len(addresses)} contract address.')

        contracts = []

        for index, address in enumerate(addresses):
            contract_info = self._get_detail_from_etherscan(
                address=address,
                cookie=self.cookie,
                api_key=self.api_key
            )

            if contract_info is not None:
                contracts.append(contract_info)

            if index != 0 and (index % 500 == 0 or index == len(addresses) - 1):
                self.logger.info(f'{index + 1} items processed, extract {len(contracts)} contracts.')

                with open(verified_contract_output_path, 'a+', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    if len(contracts) > 0:
                        writer.writerow(list(contracts[0].keys()))
                        for contract in contracts:
                            writer.writerow(list(contract.values()))

                contracts = []

        return {'verified_contract': verified_contract_output_path}

    def _get_detail_from_etherscan(self,
                                   address: str,
                                   cookie: str,
                                   api_key: str) -> Optional[Dict[str, str]]:
        address0x = f'0x{address}'

        res = requests.get(url=f'https://etherscan.io/address/{address0x}', headers={
            'authority': 'etherscan.io',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5',
            'cookie': cookie
        })
        html = etree.HTML(res.text)
        label_items = html.xpath('//*[@id="content"]/div[1]/div/div[1]/div/a')
        name_item = html.xpath('/html/body/div[1]/main/div[4]/div[1]/div[1]/div/div[1]/div/span/span')

        try:
            res = requests.get(
                url=f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address={address0x}&apikey={api_key}')
            if 'result' not in res.json() or type(res.json()['result']) is str:
                return None
        except Exception as ex:
            self.logger.error(f'{address} meets problems: {ex}')
            return None

        contract_detail = res.json()['result'][0]

        try:
            json.loads(contract_detail['ABI'])
        except Exception:
            return None

        return {
            'address': address,
            'name': name_item[0].text if len(name_item) > 0 else None,
            'namespace': label_items[0].text.replace(' ', '') if len(label_items) > 0 else None,
            'label': ','.join([label.text.replace(' ', '') for label in label_items]),
            'abi': contract_detail['ABI']
        }
