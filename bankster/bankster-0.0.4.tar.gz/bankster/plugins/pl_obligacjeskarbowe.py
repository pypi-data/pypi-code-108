#!/usr/bin/env python3

import re
import structlog
import mechanicalsoup
from urllib.parse import urljoin

class PLObligacjeSkarbowe(object):

    def __init__(self, credstore=None, **kwargs):
        self.url_base = 'https://www.zakup.obligacjeskarbowe.pl/'
        self.log = structlog.get_logger()
        self.log = self.log.bind(cls=__class__.__name__, url_base=self.url_base)

        self.credstore = credstore
        if self.credstore:
            self.log = self.log.bind(credstore=credstore.name)
            self.log.msg('bound to credentials store')

        self.browser = mechanicalsoup.StatefulBrowser()


    def usable_identities(self):
        return list(filter(lambda i: i is not None, [ self.credstore.get_identity(self.url_base) ]))


    def authenticate(self, identity=None):
        self.log.msg('authentication attempt')

        self.identity = identity or self.credstore.get_identity(self.url_base)
        self.log = self.log.bind(identity=self.identity)

        creds = self.credstore.get_credentials(self.url_base, self.identity)
        self.log.msg('got creds', password='{}.....{}'.format(creds['password'][0:2], creds['password'][-1]))

        self.browser.open(self.url_base)
        self.browser.select_form('form#login')
        self.browser['username'] = creds['identity']
        #
        # The password length in the login form is limited to 16 o_O WTF is DIS?
        # From the page source:
        # <input id="password" name="password" type="password" maxlength="16" class="ui-inputfield 
        # ui-keyboard-input ui-widget ui-state-default ui-corner-all span-5 text hasKeypad" 
        # role="textbox" aria-disabled="false" aria-readonly="false">
        #
        self.browser['password'] = creds['password'][0:16]

        self.browser.submit_selected()
        
        return True


    def get_balances(self):
        self.log.msg('fetching balances')

        account_page = self.browser.get_current_page()
        bags = []

        cash_amount = account_page.find(string='Saldo środków pieniężnych').parent.next_sibling.get_text(strip=True)
        amount = re.match('([0-9, ]+) ', cash_amount).group(1).replace(' ','').replace(',','.')

        bags.append({
            'description': 'Gotówka',
            'value': 'PLN {}'.format(amount)
        })

        bonds_table = account_page.find(string='Obligacje').find_next(class_='ui-datatable')
        bonds = []
        for bond_row in bonds_table.find_all('tr'):
            cols = bond_row.find_all('td')
            if len(cols) == 0:
                # Skip if there are no columns (likely the table header)
                continue

            bond_description = bond_row.find_all('td')[0].find('span').get_text(strip=True)

            if bond_description == 'Razem':
                # Skip the row with totals
                continue

            bond_value = bond_row.find_all('td')[4].get_text(strip=True)
            amount = re.search('([0-9, \u00a0]+)', bond_value).group(1).replace(',','.').replace('\u00a0','')
            bonds.append({
                'description': bond_description,
                'value': 'PLN {}'.format(amount)
            })

        return dict(name='Obligacje Skarbowe', bags=bags + bonds)


    def logout(self):
        self.log.msg('logout')

        self.browser.get(urljoin(self.url_base, '/logout'))


    def close(self):
        self.log.msg('closing')
        self.browser.close()

