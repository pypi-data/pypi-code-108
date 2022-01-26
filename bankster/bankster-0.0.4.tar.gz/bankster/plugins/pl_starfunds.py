#!/usr/bin/env python3

import structlog
#import mechanicalsoup
import requests
from urllib.parse import urljoin
import json
import time

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


class PLStarfunds(object):

    def __init__(self, credstore=None, **kwargs):
        self.url_base = 'https://platforma.starfunds.pl/'
        self.log = structlog.get_logger()
        self.log = self.log.bind(cls=__class__.__name__, url_base=self.url_base)

        self.credstore = credstore
        if self.credstore:
            self.log = self.log.bind(credstore=credstore.name)
            self.log.msg('bound to credentials store')

        self.s = SessionWithUrlBase(url_base=self.url_base)
        self.s.hooks = dict(response=print_all)

    def usable_identities(self):
        return list(filter(lambda i: i is not None, [ self.credstore.get_identity(self.url_base) ]))

    def authenticate(self, identity=None):
        self.log.msg('authentication attempt')

        self.identity = identity or self.credstore.get_identity(self.url_base)
        self.log = self.log.bind(identity=self.identity)

        self.creds = self.credstore.get_credentials(self.url_base, self.identity)
        self.log.msg('got creds', password='{}.....{}'.format(self.creds['password'][0:2], self.creds['password'][-1]))

        self.session_headers = dict(svauth=str(int(time.time())), tabid='null')

        # First do preauth
        preauth_resp = self.s.post('/invoker/SubjectAccountService/preLogin', data=dict(nik=self.identity), headers=self.session_headers)
        
        # Save tabid, it is the session token
        self.session_headers['tabid'] = preauth_resp.headers['tabid']

        # Now do auth
        auth_resp = self.s.post('/invoker/SubjectAccountService/login', headers=self.session_headers, data={
            'pl.starvest.interfaces.dto.subject.LoginRequestDTO': json.dumps(dict(nik=self.identity, pin=self.creds['password'])),
            'inputType': 'JSON'
        })

        return True

    def get_balances(self):
        self.log.msg('fetching balances')

        summary_resp = self.s.post('/invoker/SubjectsService/getOwnedSecuritiesForSummary', headers=self.session_headers, 
            data = {
                'pl.starvest.interfaces.dto.security.GetOwnedSecuritiesSummaryRequestDTO': json.dumps({'subjectId':0}),
                'inputType': 'JSON'
            }
        )
        summary_data = summary_resp.json()
        securities = []
        for sec in summary_data['dto']['responseObject']['securities']:
            security_name = sec['security']['name']
            currency = sec['currency']
            amount = sec['currentValueSum']
            securities.append(dict(description=security_name, value='{} {:.2f}'.format(currency, amount)))

        return dict(name='Starfunds', bags=securities)


    def logout(self):
        self.log.msg('logout')
        self.s.post('/invoker/SubjectAccountService/logout')

    def close(self):
        self.log.msg('closing')

