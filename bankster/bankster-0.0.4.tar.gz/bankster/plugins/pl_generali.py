#!/usr/bin/env python3

import structlog
import re
import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By

class PLGenerali(object):

    def __init__(self, credstore=None, **kwargs):
        self.url_base = 'https://konto.generali.pl/'
        self.log = structlog.get_logger()
        self.log = self.log.bind(cls=__class__.__name__, url_base=self.url_base)

        self.credstore = credstore
        if self.credstore:
            self.log = self.log.bind(credstore=credstore.name)
            self.log.msg('bound to credentials store')
        
        self.browser = webdriver.Firefox()

    def usable_identities(self):
        return list(filter(lambda i: i is not None, [ self.credstore.get_identity(self.url_base) ]))

    def authenticate(self, identity=None):
        self.log.msg('authentication attempt')

        self.identity = identity or self.credstore.get_identity(self.url_base)
        self.log = self.log.bind(identity=self.identity)

        creds = self.credstore.get_credentials(self.url_base, self.identity)
        self.log.msg('got creds', password='{}.....{}'.format(creds['password'][0:2], creds['password'][-1]))

        self.browser.get(self.url_base)
        login_field = self.browser.find_element(By.CSS_SELECTOR, 'form#loginModel input#login')
        login_field.send_keys(creds['identity'])
        password_field = self.browser.find_element(By.CSS_SELECTOR, 'form#loginModel input#password')
        password_field.send_keys(creds['password'])
        login_field.submit()

        time.sleep(30)

        try:
            # Close popup if it appeared
            popup = self.browser.find_element(By.CSS_SELECTOR, 'div.popup > a.close-popup')
            if popup is not None:
                popup.click()
        except selenium.common.exceptions.NoSuchElementException as e:
            pass

        return True


    def get_balances(self):
        self.log.msg('fetching balances')
        policies = []

        policy_elements = self.browser.find_elements(By.CSS_SELECTOR, 'h4.policyheader')
        for policy_element in policy_elements:
            policy_name = policy_element.find_element(By.CSS_SELECTOR, '.name').text
            policy_number = policy_element.find_element(By.CSS_SELECTOR, '.number').text
            policy_uri = policy_element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

            policies.append({
                'description': "{} {}".format(policy_name, policy_number),
                'href': policy_uri,
                'value': None
            })
    
        #
        # Get details for each policy
        #
        for policy in policies:
            policy_description = policy['description']
            
            self.log.msg("fetching info for policy", policy=policy_description)

            self.browser.get(policy['href'])

            del policy['href'] # Get rid of URIs, they are not needed in the final dataset

            try:
                value_link = self.browser.find_element(By.LINK_TEXT, 'Wartość umowy')
                value_link.click()        
            except selenium.common.exceptions.NoSuchElementException:
                # No link to see the value
                continue

            value_field = self.browser.find_element(By.XPATH, "//span[contains(.,'Aktualna wartość umowy')]")
            amount = re.search('\s([0-9,\s]+)\s', value_field.text).group(1).replace(' ','').replace(',','.')
            policy['value'] = 'PLN {}'.format(amount)

        return dict(name='Generali', bags=policies)     


    def logout(self):
        self.log.msg('logout')
        logout_link = self.browser.find_element(By.LINK_TEXT, 'Wyloguj się')
        logout_link.click()


    def close(self):
        self.log.msg('closing')
        self.browser.quit()



