#!/usr/bin/env python3
# coding: utf8


from functools import partial
import requests


class TeleBot(object):
    def __init__(self, access_token):
        self._access_token = access_token

    def __getattr__(self, method):
        return partial(self._call, method)

    def __call__(self, method, **params):
        return getattr(self, method)(**params)

    def _call(self, method, **params):
        url = f'https://api.telegram.org/bot{self._access_token}/{method}'
        return requests.post(url, params).json()

    def get_updates(self, **params):
        url = f'https://api.telegram.org/bot{self._access_token}/getUpdates'
        if 'timeout' in params:
            return requests.post(url, params, timeout=params['timeout']+5).json()
        return requests.post(url, params).json()

    def send_message(self, chat_id, message):
        url = f'https://api.telegram.org/bot{self._access_token}/sendMessage'
        params = {'chat_id': chat_id, 'text': message}
        return requests.post(url, params).json()

    def reply_message(self, chat_id, message, reply_to_message_id):
        url = f'https://api.telegram.org/bot{self._access_token}/sendMessage'
        params = {'chat_id': chat_id, 'text': message, 'reply_to_message_id': reply_to_message_id}
        return requests.post(url, params).json()

    def delete_message(self, chat_id, message_id):
        url = f'https://api.telegram.org/bot{self._access_token}/deleteMessage'
        params = {'chat_id': chat_id, 'message_id': message_id}
        return requests.post(url, params).json()


if __name__ == '__main__':
    bot = TeleBot('456941934:AAGZMmXJE4VyLagIkVY7qMG0doASxU7f8ac')
    #bot.send_message(161680036, 'Hello')
    bot.reply_message(161680036, 'reply for your message', 16394)