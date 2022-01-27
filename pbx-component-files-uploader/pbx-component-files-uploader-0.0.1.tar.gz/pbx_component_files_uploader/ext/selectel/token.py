from __future__ import annotations
from pbx_component_files_uploader.exceptions.errors import EmptyAuthField
from logging import Logger
from pathlib import Path
import time
import json


class Token:
    THRESHOLD = 300
    AUTH_TOKEN_STORAGE_FILE_NAME = 'token.selectel.json'

    def __init__(self, tokenCacheDir: str, logger: Logger):
        self.tokenCacheDir = tokenCacheDir
        if not tokenCacheDir:
            raise EmptyAuthField('token_cache_dir')
        self.logger = logger

    def load(self) -> Token:
        tokenFile = self.get_token_cache_file()

        tokenData = {'secret': '', 'storage_url': '',
                     'expires_at': int(time.time())}
        if tokenFile.is_file():
            try:
                tokenData = json.loads(tokenFile.read_text())
            except Exception as e:
                self.logger.debug('failed to load token cache from file')

        self.secret = tokenData['secret']
        self.storageUrl = tokenData['storage_url']
        self.expiresAt = tokenData['expires_at']

        return self

    def update(self) -> Token:
        self.get_token_cache_file().touch(exist_ok=True)
        self.get_token_cache_file().write_text(data=json.dumps({
            'secret': self.secret,
            'storage_url': self.storageUrl,
            'expires_at': self.expiresAt
        }), encoding='utf-8')

        return self

    def is_expired(self):
        return self.expiresAt - int(time.time()) < self.THRESHOLD

    def get_token_cache_file(self) -> Path:
        return Path(self.tokenCacheDir + '/' + Token.AUTH_TOKEN_STORAGE_FILE_NAME)
