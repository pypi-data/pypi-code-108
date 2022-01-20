import ast
import re
from typing import List

import codefast as cf
from dofast.bots.processors.base import TextProcessor
from dofast.network import Twitter
from dofast.pipe import author
from telegram import Update


class TwitterVideoDownloader(TextProcessor):
    def match(self, text: str) -> bool:
        return text.startswith('https://twitter.com/')

    def run(self, text: str, update: Update) -> bool:
        update.message.delete()
        video = "/tmp/{}.mp4".format(text.split('/')[-1])
        cf.shell('youtube-dl -f best {} -o {}'.format(text, video))
        update.message.reply_video(open(video, 'rb'), supports_streaming=True)
        cf.io.rm(video)
        return True


class TwitterBlockerProcessor(TextProcessor):
    def __init__(self) -> None:
        self.accounts = ['slp', 'elena']

    def match(self, text: str) -> bool:
        return text.startswith('https://twitter.com/')

    def run(self, text, update: Update) -> bool:
        for account_name in self.accounts:
            _auth = ast.literal_eval(author.get(account_name))
            self.api = None
            if _auth:
                self.api = Twitter(_auth['consumer_key'],
                                   _auth['consumer_secret'],
                                   _auth['access_token'],
                                   _auth['access_token_secret'])
            screen_name = re.findall(r'https://twitter.com/(.*)/status',
                                     text)[0]
            self.api.block_by_screenname(screen_name)
            cf.info('Blocked {} for {}'.format(screen_name, account_name))
        return True
