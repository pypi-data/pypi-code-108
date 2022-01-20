#!/usr/bin/env python
import random
import codefast as cf
import authc
import requests

from dofast.web import gg_gg

import sys

from requests.api import post


def post_video_to_channel():
    # Post direct video url to slippervideo channel
    if len(sys.argv) < 2:
        usage = 'Usage: slippervideo video_url <customized_link> <extra_msg>'
        print(usage)
        return

    url, short_path, extra_msg = '', '', ''
    url = sys.argv[1]
    short_path = 'slippervideo-' + sys.argv[2] if len(
        sys.argv) > 2 else 'slippervideo-{}'.format(random.randint(1000, 9999))
    if len(sys.argv) > 3:
        extra_msg = sys.argv[3]

    cf.info('url: {}'.format(url))
    cf.info('short_path: {}'.format(short_path))
    cf.info('extra_msg: {}'.format(extra_msg))

    info = authc.authc()
    token = info['hema_bot']
    chat_id = 'slippervideo'
    url = gg_gg(url, short_path)
    cf.info('url shorten to {}'.format(url))

    text = '{} {}'.format(url, extra_msg)
    api = 'https://api.telegram.org/bot{}/sendMessage?chat_id=@{}&text={}'.format(
        token, chat_id, text)
    resp = requests.get(api)
    cf.info(resp.text)
