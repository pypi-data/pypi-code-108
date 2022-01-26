#!/usr/bin/env python3

import structlog
import requests
from urllib.parse import urljoin
import getpass
import time
from bs4 import BeautifulSoup
import re

# Kudos: https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session#43882437
class SessionWithUrlBase(requests.Session):
    def __init__(self, *args, url_base=None, **kwargs):
        super(SessionWithUrlBase, self).__init__(*args, **kwargs)
        self.url_base = url_base

    def request(self, method, url, **kwargs):
        return super(SessionWithUrlBase, self).request(method, urljoin(self.url_base, url), **kwargs)

def print_all(r, *args, **kwargs):
    print("----- REQUEST ----------")
    print("{} {}".format(r.request.method, r.request.url))
    print(r.request.headers)
    print()
    print(r.request.body)
    print("-----RESPONSE ----------")
    print("{} {}".format(r.status_code, r.url))
    print(r.headers)
    print()
    print(r.content)


class PLMBank(object):

    def __init__(self, credstore=None, **kwargs):
        self.url_base = 'https://online.mbank.pl/'
        self.log = structlog.get_logger()
        self.log = self.log.bind(cls=__class__.__name__, url_base=self.url_base)

        self.credstore = credstore
        if self.credstore:
            self.log = self.log.bind(credstore=credstore.name)
            self.log.msg('bound to credentials store')

        self.s = SessionWithUrlBase(url_base=self.url_base)
        #self.s.hooks = dict(response=print_all)

    def usable_identities(self):
        return list(filter(lambda i: i is not None, [ self.credstore.get_identity(self.url_base) ]))

    def authenticate(self, identity=None):
        self.log.msg('authentication attempt')

        self.identity = identity or self.credstore.get_identity(self.url_base)
        self.log = self.log.bind(identity=self.identity)

        self.creds = self.credstore.get_credentials(self.url_base, self.identity)
        print(self.creds)
        if self.creds['password'] is None:
            self.creds['password'] = getpass.getpass("Enter password for login '{}' used to access URL '{}': ".format(self.creds['identity'], self.url_base))

        self.log.msg('got creds', password='{}.....{}'.format(self.creds['password'][0:2], self.creds['password'][-1]))

        login_resp = self.s.post('/pl/LoginMain/Account/JsonLogin', json={
            'UserName': self.creds['identity'],
            'Password': self.creds['password'],
            'Seed': '',
            'Scenario': 'Default',
            'UWAdditionalParams': {
                "InOut": None,
                "ReturnAddress": None,"Source": None
            },
            "Lang":"",
            "HrefHasHash": False,
            "DfpData": {
                "dfp":"", "scaOperationId":"", "errorMessage": None
            }
        })

        setup_data = self.s.get('/pl/setup/data').json()
        
        self.session_headers = {
            'X-Request-Verification-Token': setup_data['antiForgeryToken']
        }

        sca_auth_data = self.s.post('/pl/Sca/GetScaAuthorizationData', headers=self.session_headers).json()

        prep_auth_data = self.s.post('/api/auth/initprepare', headers=self.session_headers, json={
            "Url": "sca/authorization/disposable",
            "Method": "POST",
            "Data": {
                "ScaAuthorizationId": sca_auth_data['ScaAuthorizationId']
            }
        }).json()

        self.log.msg('waiting for authorization', devicename=prep_auth_data['DeviceName'])
        while True:
            # Check the authorization status

            auth_status_data = self.s.post('/api/auth/status', headers=self.session_headers, json={
                'TranId': prep_auth_data['TranId']
            }).json()

            self.log.msg('authorization status', status=auth_status_data['Status'])
            if auth_status_data['Status'] == 'Authorized':
                # Execute auth
                self.s.post('/api/auth/execute', headers=self.session_headers, json={})

                self.s.post('/pl/Sca/FinalizeAuthorization', headers=self.session_headers, json={
                    "scaAuthorizationId": sca_auth_data['ScaAuthorizationId']
                })

                setup_data = self.s.get('/pl/setup/data', headers=self.session_headers).json()
                self.session_headers['X-Request-Verification-Token'] = setup_data['antiForgeryToken']

                return True

            time.sleep(1)

        return True

    def get_balances(self):
        self.log.msg('fetching balances')

        #self.s.post('/pl/MyDesktop/Dashboard/GetProducts', headers=self.session_headers)

        accounts_data = self.s.post('/pl/Accounts/Accounts/List').json()
        accounts = []
        for acct in accounts_data['properties']['CurrentAccountsList']:
            account_name = acct['cProductName']
            account_subtitle = acct['cSubTitle']
            account_currency  = acct['cCurrency']
            account_amount = acct['mOwnBalance']
            accounts.append({
                'description': "{} {}".format(account_name, account_subtitle), 
                'value': '{} {}'.format(account_currency, account_amount)
            })

        investments = []
        investments_resp = self.s.post('/pl/InvestmentFunds/Dashboard/Dashboard', data=dict(type='All'), headers=self.session_headers)
        soup = BeautifulSoup(investments_resp.content)
        inv_rows = soup.find('ul', class_='sub').find_all('li', class_='investment-row')

        for inv in inv_rows:
            investment_name = inv.find('li', class_='investment-name-group').get_text(strip=True)
            investment_value = inv.find('li', class_='investment-actual').get_text(strip=True)
            # Swap currency code and value
            m = re.match('([\d.,\s]+)\s+(\w+)', investment_value)
            investment_value = '{} {}'.format(m.group(2), m.group(1).replace(',','.').replace(' ','').replace('\xa0',''))

            investments.append({
                'description': investment_name,
                'value': investment_value
            })
            
        return dict(name='MBank', bags=accounts + investments)

    def logout(self):
        self.log.msg('logout')

        self.s.get('/LoginMain/Account/Logout', headers=self.session_headers)

    def close(self):
        self.log.msg('closing')

