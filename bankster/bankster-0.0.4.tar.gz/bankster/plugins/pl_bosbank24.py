#!/usr/bin/env python3

import requests
import re
import structlog
import json
import getpass
from urllib.parse import urljoin


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


class PLBosbank(object):

    def __init__(self, credstore=None, **kwargs):
        self.url_base = 'https://bosbank24.pl/frontend-web/app/auth.html'
        self.log = structlog.get_logger()
        self.log = self.log.bind(cls=__class__.__name__, url_base=self.url_base)

        self.credstore = credstore
        if self.credstore:
            self.log = self.log.bind(credstore=credstore.name)
            self.log.msg('bound to credentials store')

        self.s = requests.Session()
        #self.s.hooks = dict(response=print_all)

    def usable_identities(self):
        return list(filter(lambda i: i is not None, [ self.credstore.get_identity(self.url_base) ]))


    def _get_xsrf_token(self):
        # Check for valid authentication token in the cookie store
        return [c.value for c in self.s.cookies if c.name == 'XSRF-TOKEN' and not c.is_expired()][0]


    def authenticate(self, identity=None):
        self.log.msg('authentication attempt')

        self.identity = identity or self.credstore.get_identity(self.url_base)
        self.log = self.log.bind(identity=self.identity)

        creds = self.credstore.get_credentials(self.url_base, self.identity)
        self.log.msg('got creds', password='{}.....{}'.format(creds['password'][0:2], creds['password'][-1]))

        # We don't care about the response here
        self.s.get(self.url_base)

        step1_params = dict(step=1)
        step1_resp = self.s.post(urljoin(self.url_base, '/frontend-web/app/j_spring_security_check'), data=step1_params)
        # We don't really care about the result of this request there is nothing to see here

        step_1to2_params = dict(step='1to2', j_username=self.identity)
        step_1to2_resp = self.s.post(urljoin(self.url_base, '/frontend-web/app/j_spring_security_check'), data=step_1to2_params)
        step_1to2_data = step_1to2_resp.json()

        auth_method = step_1to2_data['method']
        if auth_method == 'PASSWORD_MASKED_AND_SMS_CODE':

            password_mask = list(map(lambda c: c == '1', step_1to2_data['maskIn01Format']))
            chars = ''.join(filter(lambda c: password_mask.pop(0), creds['password']))

            step2_params=dict(step=2, j_username=self.identity, j_password=chars)
            xsrf_headers = {
                'X-XSRF-TOKEN': self._get_xsrf_token()
            }  
            step2_resp = self.s.post(urljoin(self.url_base, '/frontend-web/app/j_spring_security_check'), data=step2_params, headers=xsrf_headers)
            step2_data = step2_resp.json()

            step2_status = step2_data['status']
            if step2_status == 'CREDENTIALS_INCORRECT':
                self.log.msg('wrong credentials')
                return False
            elif step2_status == 'CREDENTIALS_CORRECT_BUT_NEXT_SMS_CODE_REQUIRED':
                self.log.msg('2fa requested')

                # The user should have received an SMS with the 2FA code at this point
                # Request it from the user
                sms_code = getpass.getpass('Enter 2FA code received via SMS: ')

                step3_params=dict(step='3s', j_next_sms_code=sms_code)
                xsrf_headers = {
                    'X-XSRF-TOKEN': self._get_xsrf_token(),
                }   
                step3_resp = self.s.post(urljoin(self.url_base, '/frontend-web/app/j_spring_security_check'), data=step3_params, headers=xsrf_headers)
                step3_data = step3_resp.json()

                step3_status = step3_data['status']
                if step3_status == 'CREDENTIALS_CORRECT':
                    pass
                else:
                    self.log.msg('cannot handle authentication step 3 response', response=step3_data)
                    return False
            else:
                self.log.msg('cannot handle authentication step 2 response', response=step2_data)
                return False

        else:  
            self.log.msg('unknown auth method', auth_method=auth_method)
            return False

        xsrf_headers = {
            'X-XSRF-TOKEN': self._get_xsrf_token()
        }   
        user_auth_details_resp = self.s.get(urljoin(self.url_base, '/frontend-web/api/user/get/user_authentication_details'), headers=xsrf_headers)
        self.user_auth_details = user_auth_details_resp.json()
        
        return True
       
    def get_balances(self):
        self.log.msg('fetching balances')

        account_info_params = dict(
            accessProfileId=self.user_auth_details['userIdentityId']['accessProfileId'], 
            customerId=self.user_auth_details['userIdentityId']['id'], 
            pageSize=5)
        xsrf_headers = {
            'X-XSRF-TOKEN': self._get_xsrf_token()
        }  
        account_data_resp = self.s.post(urljoin(self.url_base, '/frontend-web/api/account'), json=account_info_params, headers=xsrf_headers)
        account_data = account_data_resp.json()

        accounts = []
        for account in account_data['content']:
            account_name = account['accountName']
            account_balance = account['accessibleAssets']
            account_currency = account['currency']

            accounts.append(dict(description=account_name, value='{} {}'.format(account_currency, account_balance)) )

        return dict(name='BOS Bank', bags=accounts)

    def logout(self):
        self.log.msg('logout')



    def close(self):
        self.log.msg('closing')

