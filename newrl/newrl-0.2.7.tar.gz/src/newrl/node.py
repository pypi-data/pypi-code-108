import requests


class Node():
    def __init__(self, url='http://newrl.net:8090'):
        self.url = url

    def get_balance(self, balance_type, wallet_address, token_code):
        balance_path = '/get-balance'
        data = {
            'balance_type': balance_type,
            'wallet_address': wallet_address,
            'token_code': token_code,
        }
        response = requests.post(self.url + balance_path, json=data)
        if response.status_code != 200:
            raise Exception('Error calling node: ', response.text)
        return response.json()['balance']

    def add_wallet(
        self,
        custodian_address: str,
        jurisdiction: str,
        public_key: str,
        ownertype: str = '1',
        kyc_docs: list = [],
        specific_data: dict = {},
    ):
        data = {
            'custodian_address': custodian_address,
            'ownertype': ownertype,
            'jurisdiction': jurisdiction,
            'public_key': public_key,
            'kyc_docs': kyc_docs,
            'specific_data': specific_data,
        }

        add_wallet_path = '/add-wallet'
        response = requests.post(self.url + add_wallet_path, json=data)
        if response.status_code != 200:
            raise Exception('Error calling node: ', response.text)
        return response.json()

    def add_token(
        self,
        token_code: str,
        token_name: str,
        token_type: str,
        first_owner: str,
        custodian: str,
        legal_doc_hash: str,
        amount_created: int,
        value_created: int,
        disallowed_regions: list = [],
        token_attributes: dict = {},
        is_smart_contract_token: bool = False,
    ):
        data = {
            'token_code': token_code,
            'token_name': token_name,
            'token_type': token_type,
            'first_owner': first_owner,
            'custodian': custodian,
            'legal_doc': legal_doc_hash,
            'amount_created': amount_created,
            'value_created': value_created,
            'disallowed_regions': disallowed_regions,
            'is_smart_contract_token': is_smart_contract_token,
            'token_attributes': token_attributes
        }

        add_token_path = '/add-token'
        response = requests.post(self.url + add_token_path, json=data)
        if response.status_code != 200:
            raise Exception('Error calling node: ', response.text)
        return response.json()

    def add_transfer(
        self,
        asset1_code: int,
        asset2_code: int,
        wallet1_address: str,
        wallet2_address: str,
        asset1_qty: int,
        asset2_qty: int,
        transfer_type: int = 4,
    ):
        data = {
            'transfer_type': transfer_type,
            'asset1_code': asset1_code,
            'asset2_code': asset2_code,
            'wallet1_address': wallet1_address,
            'wallet2_address': wallet2_address,
            'asset1_qty': asset1_qty,
            'asset2_qty': asset2_qty
        }

        add_transfer_path = '/add-transfer'
        response = requests.post(self.url + add_transfer_path, json=data)
        if response.status_code != 200:
            raise Exception('Error calling node: ', response.text)
        return response.json()

    def validate_transaction(self, transaction):
        validate_transaction_path = '/validate-transaction'
        response = requests.post(
            self.url + validate_transaction_path, json=transaction)
        if response.status_code != 200:
            raise Exception('Error calling node: ', response.text)
        return response.json()

    def run_updater(self,):
        run_updater_path = '/run-updater'
        response = requests.post(self.url + run_updater_path)
        if response.status_code != 200:
            raise Exception('Error calling node: ', response.text)
        return response.text


# Basic tests during dev - To be refactored to tests
if __name__ == '__main__':
    node = Node()

    balance = node.get_balance(
        'TOKEN_IN_WALLET', '0x16031ef543619a8569f0d7c3e73feb66114bf6a0', 10)
    print(balance)

    from .wallet import generate_wallet_address
    wallet = generate_wallet_address()

    wallet_add_transaction = node.add_wallet(
        wallet['address'], '910', wallet['public'], 1)

    print(wallet_add_transaction)

    from .signer import sign_transaction

    signed_wallet_add_transaction = sign_transaction(
        wallet, wallet_add_transaction)
    print(signed_wallet_add_transaction)

    token_add_transaction = node.add_token(
        'my_new_token',
        '1',
        '0x16031ef543619a8569f0d7c3e73feb66114bf6a0',
        '0x16031ef543619a8569f0d7c3e73feb66114bf6a0',
        'fhdkfhldkhf',
        10000,
        10000,
    )

    signed_token_add_transaction = sign_transaction(
        wallet, token_add_transaction)
    print(signed_token_add_transaction)

    transfer_transaction = node.add_transfer(
        9, 10, '0x16031ef543619a8569f0d7c3e73feb66114bf6a0', '0x16031ef543619a8569f0d7c3e73feb66114bf6a0', 10, 10, 4)
    signed_transfer = sign_transaction(wallet, transfer_transaction)
    print(signed_transfer)

    validate_result = node.validate_transaction(signed_transfer)
    print(validate_result)

    print(node.run_updater())
