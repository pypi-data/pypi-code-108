#!/usr/bin/env python3

import structlog
import mechanicalsoup
import getpass
from urllib.parse import urljoin
from http.cookiejar import LWPCookieJar
from pathlib import Path
from xdg import XDG_CACHE_HOME

class PLIdeabank(object):

    def __init__(self, credstore=None, **kwargs):
        self.sso_url_base = 'https://sso.cloud.ideabank.pl/'
        self.cloud_url_base = 'https://cloud.ideabank.pl/'
        self.log = structlog.get_logger()
        self.log = self.log.bind(cls=__class__.__name__, sso_url_base=self.sso_url_base, cloud_url_base=self.cloud_url_base)

        self.credstore = credstore
        if self.credstore:
            self.log = self.log.bind(credstore=credstore.name)
            self.log.msg('bound to credentials store')

        self.browser = mechanicalsoup.StatefulBrowser()


    def _get_auth_token(self):
        # Check for valid authentication token in the cookie store
        return [c.value for c in self.cookiejar if c.name == 'Authentication-Token' and not c.is_expired()][0]


    def _we_have_cookie(self, n):
        return len([c.value for c in self.cookiejar if c.name == n and not c.is_expired()]) > 0


    def _sso_authenticate(self):
        self.log.msg('sso auth')

        # sso_login_info = self.browser.get(urljoin(self.sso_url_base, '/authenticate/login'), params={ 'login': login })
        self.browser.open(self.sso_url_base)

        sso_auth_params=dict(login=self.creds['identity'], password=self.creds['password'])
        sso_auth_resp = self.browser.post(urljoin(self.sso_url_base, '/authenticate/login'),
                                    json=sso_auth_params)
        self.cookiejar.save()
        return sso_auth_resp.json()['token']


    def _perform_2fa(self, sso_token):
        # The twofactor info is not known in the beginning
        twofactor = None

        while True:
            headers = {'Exchange-Token': sso_token}

            if twofactor is not None:
                headers.update(twofactor)

            # Claim device is trusted
            trusted_dev_claim_res = self.browser.post(urljoin(self.cloud_url_base, '/api/strong-authentication'),
                                                json={'trustedDevice': True}, headers=headers)
            self.cookiejar.save()

            # Check if claim was successful
            if self._we_have_cookie('ib_trusted_device'):
                break
            else:
                # Check for what to do now
                claim_resp = trusted_dev_claim_res.json()

                if claim_resp['code'] == 'MISSING_VERIFICATION_CODE':
                    code_number = claim_resp['content']['codeNumber']
                    code_date = claim_resp['content']['generatedDate']

                    twofactor = {'Verification-Code-Number': str(code_number)}

                    # The user should have received an SMS with the 2FA code at this point
                    # Request it from the user
                    twofactor_code = getpass.getpass(
                        'Enter 2FA code number {} generated on {}: '.format(code_number, code_date))
                    twofactor['Verification-Code'] = twofactor_code

                else:
                    self.log.msg('unrecognized trusted device claim response code',
                            code=claim_resp['code'])
                    raise RuntimeError()


    def usable_identities(self):
        return list(filter(lambda i: i is not None, [ self.credstore.get_identity(self.sso_url_base) ]))


    def authenticate(self, identity=None):
        self.log.msg('authentication attempt')

        self.identity = identity or self.credstore.get_identity(self.sso_url_base)
        self.log = self.log.bind(identity=self.identity)

        self.creds = self.credstore.get_credentials(self.sso_url_base, self.identity)
        self.log.msg('got creds', password='{}.....{}'.format(self.creds['password'][0:2], self.creds['password'][-1]))

        # Load cookiejar
        cache_dir = Path(XDG_CACHE_HOME, 'ideabank-fetch-balances', self.creds['identity'])
        cache_dir.mkdir(parents=True, exist_ok=True)

        cookiejar_filename = Path(cache_dir, 'cookies.txt')
        self.cookiejar = LWPCookieJar(str(cookiejar_filename))
        if cookiejar_filename.exists():
            self.cookiejar.load()
        
        # Use the cookiejar we just loaded 
        self.browser.set_cookiejar(self.cookiejar)

        # Check if the authentication token we have is valid
        if self._we_have_cookie('Authentication-Token'):
            self.session_headers = {'Authentication-Token': self._get_auth_token()}

            user_info_resp = self.browser.get(
                urljoin(self.cloud_url_base, '/api/user/profile.json'), headers=self.session_headers)

            if not user_info_resp.ok:
                self.log.msg('session token not valid, authenticating')

                # The cached token is not valid, remove it from the cookie store
                self.cookiejar.clear('.cloud.ideabank.pl', '/', 'Authentication-Token')

        # Check if we have an authentication token
        if not self._we_have_cookie('Authentication-Token'):
            # Authenticate, we do not have a valid token

            # First do SSO
            sso_token = self._sso_authenticate()

            # Now attempt to authenticate to main application (Cloud)
            cloud_auth_resp = self.browser.post(
                urljoin(self.cloud_url_base, '/api/login'), data={'token': sso_token})
            self.cookiejar.save()

            # We need to perform 2FA if no token at this point
            if not self._we_have_cookie('Authentication-Token'):
                self.log.msg('no auth token')

                final_uri = cloud_auth_resp.url
                self.log.msg('redirected', redirect_uri=final_uri)

                # We have no token, check if we were redirected to the 2FA page
                if final_uri != urljoin(self.cloud_url_base, '/strong-authentication'):
                    # The target URI is not what we expected
                    self.log.msg('unexpected 2fa URI')
                    return False

                self._perform_2fa(sso_token)

                # Try to get the cloud token again
                cloud_auth_resp = self.browser.post(
                    urljoin(self.cloud_url_base, '/api/login'), data={'token': sso_token})
                self.cookiejar.save()

                if not self._we_have_cookie('Authentication-Token'):
                    self.log.msg("cannot authenticate after 2FA")
                    return False

            self.session_headers = {'Authentication-Token': self._get_auth_token()}
            return True

        return True


    def get_balances(self):
        self.log.msg('fetching balances')

        # user_info_resp = self.browser.get(urljoin(self.cloud_url_base, '/api/user/profile.json'), headers=session_headers)
        # print(json.dumps(user_info_resp.json(), indent=2))

        accounts = []
        accounts_info_resp = self.browser.get(
            urljoin(self.cloud_url_base, '/api/accounts'), headers=self.session_headers)
        # print(json.dumps(accounts_info_resp.json(), indent=2))
        for acct_group in accounts_info_resp.json()['personAccountGroups']:
            for account in acct_group['accounts']:
                name = account['accountName']
                balance = account['activeBalance']
                accounts.append({
                    'description': name,
                    'value': 'PLN {}'.format(balance)
                })

        deposits = []
        deposits_info_resp = self.browser.get(urljoin(self.cloud_url_base, '/api/deposits'), headers=self.session_headers,
                                        params={
            'status': 'ACTIVE'
        })
        # print(json.dumps(deposits_info_resp.json(), indent=2))
        for deposit in deposits_info_resp.json()['deposits']:
            name = deposit['name']
            amount = deposit['amount']
            deposits.append({
                'description': name,
                'value': 'PLN {}'.format(amount)
            })

        return dict(name='Ideabank', bags=accounts + deposits)


    def logout(self):
        self.log.msg('logout')

        self.browser.get(urljoin(self.cloud_url_base, '/api/logout'),
                    headers=self.session_headers)
        self.cookiejar.save()


    def close(self):
        self.log.msg('closing')

        self.browser.close()

