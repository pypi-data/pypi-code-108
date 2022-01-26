#!/usr/bin/env python3

import requests
import structlog
from urllib.parse import urljoin

class PLNestbank(object):

    def __init__(self, credstore=None, **kwargs):
        self.url_base = 'https://login.nestbank.pl/login'
        self.log = structlog.get_logger()
        self.log = self.log.bind(cls=__class__.__name__, url_base=self.url_base)

        self.credstore = credstore
        if self.credstore:
            self.log = self.log.bind(credstore=credstore.name)
            self.log.msg('bound to credentials store')

        self.s = requests.Session()


    def usable_identities(self):
        return list(filter(lambda i: i is not None, [ self.credstore.get_identity(self.url_base) ]))


    def authenticate(self, identity=None):
        self.log.msg('authentication attempt')

        self.identity = identity or self.credstore.get_identity(self.url_base)
        self.log = self.log.bind(identity=self.identity)

        creds = self.credstore.get_credentials(self.url_base, self.identity)
        self.log.msg('got creds', password='{}.....{}'.format(creds['password'][0:2], creds['password'][-1]))

        login_form = self.s.get(self.url_base)

        auth_resp = self.s.post(urljoin(self.url_base, '/rest/v1/auth/loginByFullPassword'),
                            json={
            'login': creds['identity'],
            'password': creds['password'],
            'avatarId': creds['custom_properties']['avatarId'],
            'loginScopeType': 'WWW'
        })
        
        session_token = auth_resp.headers.get('Session-Token', None)
        if session_token is None:
            self.log.msg('login failed', response=auth_resp.json())
            return False

        self.auth_resp = auth_resp
        self.auth_headers = { 'Session-Token': session_token }
        return True

    
    def get_balances(self):
        self.log.msg('fetching balances')

        accounts = []
        for context in self.auth_resp.json()['userContexts']:
            context_id = context['id']

            accounts_info_resp = self.s.get(urljoin(self.url_base, '/rest/v1/context/{}/account'.format(context_id)),
                                    headers=self.auth_headers)

            for account in accounts_info_resp.json():
                account_name = account['name']
                account_currency = account['currency']
                account_balance = account['balance']

                accounts.append({
                    'description': account_name,
                    'value': '{} {}'.format(account_currency, account_balance)
                })

        return dict(name='Nest Bank', bags=accounts)


    def logout(self):
        self.log.msg('logout')

        self.s.get(urljoin(self.url_base, '/rest/v1/auth/logout'), headers=self.auth_headers)


    def close(self):
        self.log.msg('closing')

