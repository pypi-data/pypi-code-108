from web3 import Web3
import json
from decimal import Decimal

# internal
from db_utility import Query
from pricing import priceData


class Crypto():
    def __init__(self, db):

        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/80de2f7c4deb45d5a880a822f2bb1e5d'))
        # define ERC20 contract
        self.erc20_abi = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],'
                                    '"payable":false,"stateMutability":"view","type":"function"},{"constant":false,'
                                    '"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],'
                                    '"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,'
                                    '"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],'
                                    '"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,'
                                    '"stateMutability":"view","type":"function"},{"constant":false,'
                                    '"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value",'
                                    '"type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],'
                                    '"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],'
                                    '"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,'
                                    '"stateMutability":"view","type":"function"},{"constant":true,'
                                    '"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf",'
                                    '"outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view",'
                                    '"type":"function"},{"constant":true,"inputs":[],"name":"symbol",'
                                    '"outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view",'
                                    '"type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},'
                                    '{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],'
                                    '"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,'
                                    '"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],'
                                    '"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,'
                                    '"stateMutability":"view","type":"function"},{"anonymous":false,'
                                    '"inputs":[{"indexed":true,"name":"_from","type":"address"},'
                                    '{"indexed":true,"name":"_to","type":"address"},'
                                    '{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},'
                                    '{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},'
                                    '{"indexed":true,"name":"_spender","type":"address"},'
                                    '{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')

        self.db = db
        self.crypto_table = 'crypto'
        self.holdings_table = 'crypto_holdings'
        # get holdings from database
        self.holdings = self.db.conn.cursor().execute("SELECT * FROM " + self.holdings_table).fetchall()
        # get wallet address from db
        self.wallet_addy = self.db.conn.cursor().execute("SELECT num FROM accounts WHERE institution = '"
                                                         + self.crypto_table + "'").fetchall()[0][0]

    def update_holdings(self,):
    #     # get wallet address from db
    #     wallet_addy = self.db.conn.cursor().execute("SELECT num FROM accounts WHERE institution = "
    #                                                 + self.crypto_table + "'").fetchall()[0][0]
    #
    #     # get holdings from database
    #     holdings = self.db.conn.cursor().execute("SELECT * FROM " + self.holdings_table).fetchall()

        # create dictionary with holdings table schema as keys
        holding = dict()
        # holding = {key: None for key in db.schema['crypto_holdings']}

        for entry in self.holdings:
            for i in range(0, len(entry)):
                holding[self.db.schema['crypto_holdings'][i]] = entry[i]

            update = {key: None for key in self.db.schema[self.crypto_table]}
            update['desc'] = holding['desc']

            # get token quantity using native decimal count ether is special case
            if holding['desc'] == 'ether':
                wei_balance = self.w3.eth.get_balance(self.wallet_addy)
                eth_balance = self.w3.fromWei(wei_balance, 'ether')
                update['qty'] = float(eth_balance)
            else:
                token = self.w3.eth.contract(address=holding['chain_address'], abi=self.erc20_abi)
                token_dec = token.functions.decimals().call()
                token_balance = token.functions.balanceOf(self.wallet_addy).call()
                token_balance = token_balance/Decimal(10 ** token_dec)

                update['qty'] = float(token_balance)

            price_data = priceData(symbol=holding['symbol'])
            update['price'] = price_data.price
            update['total'] = update['qty'] * update['price']

            update_filtered = {k: v for k, v in update.items() if v is not None}

            update_cols = list(update_filtered.keys())
            update_vals = (list(update_filtered.values()))
            #
            # query = db.insert(table='crypto', columns=update_cols, values=update_vals)
            # db.conn.cursor().execute(query, update_vals)

            query = Query(db=self.db, table=self.crypto_table,
                          in_vals=update_vals, in_cols=update_cols)
            self.db.conn.cursor().execute(query.build_insert())
            self.db.conn.commit()
