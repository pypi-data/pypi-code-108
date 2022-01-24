import json
import sys
from base64 import b64decode, b64encode
from typing import List, Optional

import codefast as cf
import joblib
import redis
from uuidentifier import snowflake

from dofast.pipe import author
from dofast.vendor.command import Command


class RedisSync(Command):
    def __init__(self):
        super().__init__()
        self.session_file = cf.io.dirname() + '/redis_sync_session.joblib'
        self.name = 'redis_sync'
        self.description = 'Sync data between Redis and local file system.'
        self.subcommands = [['st', 'sync_to_redis'], ['sf', 'sync_from_redis']]
        self.__cli = None

    @property
    def cli(self) -> redis.StrictRedis:
        """Redis client."""
        if not self.__cli:
            acc: dict
            try:
                acc = joblib.load(self.session_file)
            except Exception as e:
                cf.warning('Failed to load session file: {}'.format(e))
                acc = json.loads(author.get('DATA_REDIS').replace('\'', '"'))
                joblib.dump(acc, self.session_file)

            self.__cli = redis.StrictRedis(host=acc['host'],
                                           port=acc['port'],
                                           password=acc['password'])
        return self.__cli

    def sync_from_redis(self) -> True:
        for k, v in self.cli.hgetall(self.name).items():
            cf.info('sync from server: {}'.format(k))
            with open(k, 'wb') as fp:
                fp.write(v)
        cf.info('sync complete')
        return True

    def sync_to_redis(self, files: List[str]) -> bool:
        """Encode file to binary and store in Redis."""
        for old_key in self.cli.hkeys(self.name):
            self.cli.hdel(self.name, old_key)

        for f in files:
            cf.info('sync to server: {}'.format(f))
            with open(f, 'rb') as fp:
                self.cli.hset(self.name, cf.io.basename(f), fp.read())
        cf.info('sync complete')
        return True

    def _process(self, args: None) -> bool:
        if not args:
            self.sync_from_redis()
        else:
            self.sync_to_redis(args)

    def sync_message(self, msg: Optional[str]) -> None:
        if msg:
            self.cli.set('SYNC_MESSAGE', msg)
        else:
            print(self.cli.get('SYNC_MESSAGE').decode())


def msg():
    args = sys.argv[1] if len(sys.argv) > 1 else None
    RedisSync().sync_message(args)


def entry():
    RedisSync()._process(sys.argv[1:])
