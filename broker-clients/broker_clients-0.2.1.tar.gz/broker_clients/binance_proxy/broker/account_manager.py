import argparse
import logging
from getpass import getpass
from sqlalchemy import or_
from broker_clients import session
from broker_clients import Accounts
from binance.client import Client
from broker_clients.quantfury_proxy.broker.client import Quantfury


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinanceAuth:
    @classmethod
    def are_valid_tokens(cls, api_key, secret_key):
        client = Client(api_key=api_key, api_secret=secret_key, tld='vision')
        account = client.get_account()
        if 'canWithdraw' not in account:
            logger.info('func=Accounts.are_valid_tokens, msg=Invalid tokens')
            return False
        elif account.get('canWithdraw'):
            logger.info('func=Accounts.are_valid_tokens, msg=Excessive permissions')
            return False
        else:
            return True

    @classmethod
    def create(cls, name, api_key, secret_key):
        account = session.query(Accounts).filter(or_(
            Accounts.name == name, Accounts.api_key == api_key, Accounts.secret_key == secret_key)).first()

        if not cls.are_valid_tokens(api_key, secret_key):
            return False
        if account:
            logger.info(
                'func=Accounts.create_account, msg=Balance (name api_key secret_key) combination already exists')
            return False
        account = Accounts(name=name, api_key=api_key, secret_key=secret_key, broker_name='binance')
        session.add(account)
        session.commit()
        if not cls.are_valid_tokens(account.api_key, account.secret_key):
            logger.error('func=Accounts.create_account, msg=Cipher error')
            return False

        return True


class QuantfuryAuth:
    @classmethod
    def generate_new_token(cls, api_key, secret_key):

        login_result = Quantfury.login(api_key, secret_key)
        if 'data' in login_result and 'token' in login_result['data']:
            return login_result['data']['token']
        else:
            logger.info('func=Accounts.are_valid_tokens, msg=Invalid tokens')
            return False

    @classmethod
    def create(cls, name, api_key, secret_key):
        account = session.query(Accounts).filter(or_(
            Accounts.name == name, Accounts.api_key == api_key)).first()

        token = cls.generate_new_token(api_key, secret_key)
        if not token:
            logger.error('func=Accounts.create_account, msg=Invalid Token')
            return False
        if account and token:
            account.token = token
            logger.info(
                'func=Accounts.create_account, msg=token updated')
        else:
            account = Accounts(name=name, api_key=api_key, secret_key=secret_key, token=token, broker_name='quantfury')
            session.add(account)
        session.commit()

        return True

    @classmethod
    def update(cls, id_name):
        if type(id_name) is str:
            account = session.query(Accounts).filter(Accounts.name == id_name).first()
        else:
            account = session.query(Accounts).filter(Accounts.account_id == id_name).first()

        if not account:
            logger.error('func=Accounts.update, account_id_name={}, msg=Invalid account name'.format(id_name))
            raise ValueError('Invalid account name')

        token = cls.generate_new_token(account.api_key, account.secret_key)
        if not token:
            logger.error('func=Accounts.update, account_id_name={}, msg=Invalid Credentials'.format(id_name))
            raise ValueError('Invalid Credentials')
        account.token = token
        session.commit()

        return True


def parse_args():
    parser = argparse.ArgumentParser(description='Crate account')
    parser.add_argument('--broker', dest='broker', required=True, choices=['binance', 'quantfury'],
                        help='Broker of trading')
    parser.add_argument('--name', dest='name', required=True,
                        help='Account name')
    parser.add_argument('--api_key', dest='api_key', required=True,
                        help='API key or username')

    args = parser.parse_args()

    return args


def command():
    args = parse_args()

    args.secret_key = getpass("secret_key:")
    auth = args.broker
    if auth == 'binance':
        auth = BinanceAuth()
    else:
        auth = QuantfuryAuth()

    if auth.create(args.name, args.api_key, args.secret_key):
        logger.info('func=__main__, msg=Account created')


if __name__ == '__main__':
    command()
