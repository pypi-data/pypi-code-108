# -*- coding: utf-8 -*-

from mailin import Mailin
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implementer
import logging

from collective.sendinblue.exceptions import BadResponseError
from collective.sendinblue.exceptions import SendinblueException
from collective.sendinblue.interfaces import ISendinblueAPI
from collective.sendinblue.interfaces import ISendinblueSettings

_marker = object()
logger = logging.getLogger('collective.sendinblue')

API_URL = "https://api.sendinblue.com/v2.0"


@implementer(ISendinblueAPI)
class SendinblueAPI(object):
    """Utility for Sendinblue API calls"""

    key_accounts = "collective.sendinblue.cache.accounts"
    key_lists = "collective.sendinblue.cache.lists"

    def __init__(self):
        self.registry = None
        self.settings = None
        self.api_keys = []

    def initialize(self):
        """Load settings from registry"""
        if self.registry is None:
            self.registry = getUtility(IRegistry)
        if self.settings is None:
            self.settings = self.registry.forInterface(ISendinblueSettings)
        self.api_keys = self.settings.api_keys

    def connect(self, api_key):
        """Create client"""
        client = Mailin(API_URL, api_key)
        return client

    def parse_response(self, response):
        """Parse Sendinblue response format"""
        if not type(response) is dict:
            raise BadResponseError(response)
        code = response.get('code', None)
        if code is None:
            raise BadResponseError(response)
        message = response.get('message', None)
        if code == 'failure':
            raise SendinblueException(code, message)
        data = response.get('data', None)
        return data

    def lists(self):
        """Retrieves lists (cached)"""
        self.initialize()
        cache = self.registry.get(self.key_lists, _marker)
        if cache and cache is not _marker:
            return cache
        return self._lists()

    def _lists(self):
        """The actual API call for lists"""
        lists = {}
        for api_key in self.api_keys:
            client = self.connect(api_key)
            try:
                response = client.get_lists(50)
                data = self.parse_response(response)
                for listinfo in data:
                    id = listinfo.get('id')
                    response = client.get_list({'id': id})
                    listdata = self.parse_response(response)
                    if api_key in lists:
                        lists[api_key].append(listdata)
                    else:
                        lists[api_key] = [listdata]
            except BadResponseError:
                logger.exception("Exception getting list details.")
        return lists

    def subscribe(self, account_id, list_id, email_address):
        """API call to create a contact and subscribe it to a list"""
        self.initialize()
        client = self.connect(account_id)
        try:
            response = client.create_update_user({'email': email_address})
            data = self.parse_response(response)
        except BadResponseError:
            logger.exception("Exception creating user %s" % email_address)
            return
        try:
            response = client.add_users_list({'id': list_id,
                                              'users': [email_address]})
            data = self.parse_response(response)
        except BadResponseError:
            logger.exception("Exception subscribing %s" % email_address)
            return
        if len(data.get('success').get('users')) == 1:
            return True
        else:
            return False

    def accounts(self):
        """Retrieves accounts details (cached)"""
        self.initialize()
        cache = self.registry.get(self.key_accounts, _marker)
        if cache and cache is not _marker:
            return cache
        return self._accounts()

    def _accounts(self):
        """The actual API call for accounts"""
        accounts = {}
        for api_key in self.api_keys:
            client = self.connect(api_key)
            try:
                response = client.get_account()
                account = self.parse_response(response)
                accounts[api_key] = account
            except BadResponseError:
                logger.exception("Exception getting account details.")
        return accounts

    def updateCache(self):
        """
        Update cache of data from the sendinblue server. First reset
        our sendinblue object, as the user may have picked a
        different api key. Alternatively, compare
        self.settings.api_keys and self.sendinblue.api_keys.
        """
        self.initialize()
        if not self.settings.api_keys:
            return
        # Note that we must call the _underscore methods. These
        # bypass the cache and go directly to Sendinblue, so we are
        # certain to have up to date information.
        accounts = self._accounts()
        lists = self._lists()

        # Now save this to the registry, but only if there are
        # changes, otherwise we would do a commit every time we look
        # at the control panel.
        if type(accounts) is dict:
            if self.registry[self.key_accounts] != accounts:
                self.registry[self.key_accounts] = accounts
        if type(lists) is dict:
            if self.registry[self.key_lists] != lists:
                self.registry[self.key_lists] = lists
