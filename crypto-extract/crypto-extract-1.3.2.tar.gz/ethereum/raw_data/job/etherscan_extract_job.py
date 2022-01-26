import logging
import os.path
from typing import Dict, Optional

import requests
from lxml import etree

from ethereum.raw_data.aws_utils import AWSUtil
from ethereum.raw_data.job.base_job import BaseJob
from ethereum.raw_data.job.extract_job import init_aws_util


class EtherscanExtractJob(BaseJob):
    logger = logging.getLogger(__name__)

    aws_util: AWSUtil

    cookie: str

    api_key: str

    def __init__(self,
                 workspace_dir: str,
                 cookie: str,
                 api_key: str):
        super().__init__('etherscan_extract', 0, 0, workspace_dir)
        self.aws_util = init_aws_util(workspace_dir)
        self.cookie = cookie
        self.api_key = api_key

    def run(self):
        unverified_address = self._get_unverified_contract_address()
        self.logger.info(f'>>>>>>>>>> Start to get {len(unverified_address)} contracts. <<<<<<<<<<')
        contracts = []
        address_list = []

        for index, address in enumerate(unverified_address):
            contract = self._get_detail_from_etherscan(address, self.cookie, self.api_key)

            address_list.append(address)

            if contract is not None:
                contracts.append(contract)

            if index != 0 and (index % 50 == 0 or index == len(unverified_address) - 1):
                if len(contracts) > 0:
                    self._insert_multi_contracts(contracts)

                self._cache_multi_address(address_list)

                self.logger.info(f'{index} items processed, extract {len(contracts)} contracts.')
                contracts = []
                address_list = []

    def _cache_multi_address(self, address_list: [str]):
        cache_file_path = self._get_cache_file_path()

        with open(cache_file_path, 'a') as wf:
            for address in address_list:
                wf.write(f'{address}\n')

    def _insert_multi_contracts(self, contracts: [Dict]):
        multi_contracts_str = ','.join([f'({",".join(list(contract.values()))})' for contract in contracts])
        self.aws_util.exec_query_commit(multi_contracts_str)

    def _get_unverified_contract_address(self) -> [str]:
        all_address = self.aws_util.exec_query_get_result("""
            select address from ethereum.raw_contracts where length(bytecode)>0
            except
            select address from ethereum.verified_contracts
        """)
        all_address = set(t[0] for t in all_address)

        cache_file_path = self._get_cache_file_path()
        cache_address = set()

        if os.path.isfile(cache_file_path):
            with open(cache_file_path, 'r') as f:
                while True:
                    try:
                        line = next(f)
                        cache_address.add(line)
                    except StopIteration:
                        break

        return list(all_address - cache_address)

    def _get_cache_file_path(self):
        return f'{self.workspace_dir}/etherscan_cache.txt'

    @staticmethod
    def _get_detail_from_etherscan(address: str, cookie: str, api_key: str) -> Optional[Dict[str, str]]:
        res = requests.get(url=f'https://etherscan.io/address/{address}', headers={
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
                url=f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={api_key}')
            if 'result' not in res.json() or type(res.json()['result']) is str:
                return None
        except Exception as ex:
            print(f'{address} meets problems: {ex}')
            return None

        contract_detail = res.json()['result'][0]

        return {
            'address': f"'{address[2:]}'",
            'name': f"'{name_item[0].text}'" if len(name_item) > 0 else None,
            'namespace': f"'{label_items[0].text.replace(' ', '')}'" if len(label_items) > 0 else None,
            'label': f"'{','.join([label.text.replace(' ', '') for label in label_items])}'",
            'abi': f"'{contract_detail['ABI']}'"
        }
