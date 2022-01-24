#!/usr/bin/env python
from typing import List, Tuple, Union

import codefast as cf
from codefast import utils

from dofast.flask.config import AUTH_KEY
from dofast.oss import Bucket
from dofast.pipe import author
from dofast.security._hmac import generate_token
from dofast.utils import DeeplAPI
from dofast.vendor.command import Command, Context

cf.logger.level = 'info'


class OSSCommand(Command):
    '''OSS manager'''
    def __init__(self):
        super().__init__()
        self.name = 'oss'
        self.subcommands = [['list_files', 'list', 'ls', 'l'],
                            ['del', 'delete', 'rm'], ['up', 'upload', 'u'],
                            ['dw', 'd', 'download', 'down']]

        self.cli = Bucket()
        self.description = 'OSS manager.'

    def upload(self, files: List[str]):
        for f in files:
            cf.info('uploading file {}'.format(f))
            self.cli.upload(f)

    def download(self, files: List[str]):
        for f in files:
            cf.info('downloading file {}'.format(f))
            f = cf.io.basename(f)
            self.cli.download(f, f)

    def list_files(self, sort_by_size: bool = False):
        cf.info(self.cli.url_prefix)
        if sort_by_size:
            self.cli.list_files_by_size()
        else:
            self.cli.list_files()


class DeeplTranlationCommand(Command):
    def __init__(self):
        super().__init__()
        self.name = 'deepl'
        self.description = 'Translate Text or Document with DeepL API.'

    def _process(self, texts: List[str]) -> str:
        cli = DeeplAPI()
        if not texts:
            cli.stats
            return
        _f = lambda t: cli.document(t) if cf.io.exists(t) else cli.translate(t)
        for cand in texts:
            cf.info('DeepL translating: {}'.format(cand))
            _f(cand)


class FileInfo(Command):
    def __init__(self):
        super().__init__()
        self.name = 'fileinfo'
        self.description = 'Query audio file information.'

    def _process(self, files: List[str]):
        for f in files:
            cf.info('Query file info: {}'.format(f))
            info = cf.io.info(f)
            for key in ('bit_rate', 'channel_layout', 'channels',
                        'codec_tag_string', 'codec_long_name', 'codec_name',
                        'duration', 'filename', 'format_name', 'sample_rate',
                        'size', 'width'):
                print('{:<20} {}'.format(key, info.get(key, None)))


class Downloader(Command):
    def __init__(self):
        super().__init__()
        self.name = 'downloader'
        self.description = 'Downloader implemented with request.'

    def _process(self, urls: List[str]):
        for url in urls:
            cf.info('Downloading url {}'.format(url))
            cf.net.download(url)


class TweetPoster(Command):
    def __init__(self):
        super().__init__()
        self.name = 'tweetposter'
        self.description = 'A tweet poster.'

    def __update_entity(self, e: str, text: str, media: List[str],
                        url: str) -> Tuple[str, List[str]]:
        if e.endswith(('.png', '.jpeg', '.jpg', '.mp4', '.gif')):
            media.append(cf.io.basename(e))
            cf.net.post(url, files={'file': open(e, 'rb')})
        elif e.endswith(('.txt', '.dat')):
            text += cf.io.reads(e)
        else:
            cf.warning("Unsupported media type", e)
        return text, media

    def is_tweet_len_valid(self, text: str) -> bool:
        _len = lambda c: 2 if cf.nstr(c).is_cn() else 1
        all_len = sum(map(_len, text))
        if all_len > 280:
            cf.warning(f'Content too long with length {all_len}')
            return False
        return True

    def _process(self, args: List[str]):
        text, media = '', []
        _host = author.get('TWITTER_CLIENT')
        _receiver = '{}:8899'.format(_host)
        _client = '{}:6363/tweet'.format(_host)

        for e in args:
            if cf.io.exists(e):
                text, media = self.__update_entity(e, text, media, _receiver)
            else:
                text += e

        if self.is_tweet_len_valid(text):
            text = cf.utils.cipher(AUTH_KEY, text)
            res = cf.net.post(
                _client,
                json={
                    'text': text,
                    'media': media
                },
                params={'token': generate_token(AUTH_KEY, expire=20)})
            cf.info(res, res.text)
            assert res.text == 'SUCCESS', 'Webo post failed.'


def app():
    cont = Context()
    cont.add_command('oss', OSSCommand)
    cont.add_command('deepl', DeeplTranlationCommand)
    cont.add_command(['fileinfo', 'fi'], FileInfo)
    cont.add_command(['downloader', 'dw'], Downloader)
    cont.add_command(['tweet', 'tt'], TweetPoster)
    cont.execute()
