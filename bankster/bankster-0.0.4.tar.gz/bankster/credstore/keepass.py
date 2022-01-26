#!/usr/bin/env/python3

import structlog
import getpass

class Credstore(object):

    def __init__(self):
        self.log = structlog.get_logger()
    
    @property
    def name(self):
        raise NotImplementedError

    def unlock(self):
        raise NotImplementedError

    def get_identity(self, url):
        raise NotImplementedError
    
    def get_credentials(self, identity):
        raise NotImplementedError


class AskUserCredstore(Credstore):
    def __init__(self, identity):
        super().__init__()
        self.identity = identity
        self.log = self.log.bind(cls=__class__.__name__, identity=self.identity)

    @property
    def name(self):
        return 'keyboard-interactive'

    def unlock(self):
        return True

    def get_identity(self, url):
        return self.identity
    
    def get_credentials(self, url, identity):
        password = getpass.getpass("Enter password for login '{}' used to access URL '{}': ".format(identity, url))
        return dict(identity=identity, password=password, custom_properties={})

class KeepassCredstore(Credstore):

    def __init__(self, filename=None):
        super().__init__()
        self.filename = filename
        self.log = self.log.bind(cls=__class__.__name__, filename=self.filename)
        self.db = None

    @property
    def name(self):
        return self.filename

    def unlock(self, unlock_secret=None):
        self.log.msg('unlocking')
        try:
            from pykeepass import PyKeePass

            if unlock_secret is None:
                unlock_secret = getpass.getpass("Enter password to unlock Keepass database '{}': ".format(self.filename))
            self.db = PyKeePass(self.filename, password=unlock_secret)

            self.log.msg('loaded keepass file', entry_count=len(self.db.entries))
            return True

        except ImportError as err:
            self.log.msg('keepass load error, pykeepass module missing')
            return False

        except Exception as e:
            self.log.msg('keepass error, password is likely wrong', exc=e)
            self.db = None
            return False

    def get_identity(self, url):
        log = self.log.bind(url=url)
        log.msg('looking for identity')

        entries = self.db.find_entries(url=url, group=self.db.find_groups(name='Root', first=True))
        if len(entries) > 1:
            log.msg("multiple entries found, please specify identity manually", paths=[e.path for e in entries])
            return None
        elif len(entries) == 0:
            log.msg('no matching entries found')
            return None
        else:
            entry = next(iter(entries))
            log.msg('found entry', uuid=entry.uuid, path=entry.path)
            return entry.username

        return None


    def get_credentials(self, url, identity):
        log = self.log.bind(url=url, identity=identity)
        log.msg('looking for credentials')

        entry = self.db.find_entries(url=url, username=identity, first=True)
        if entry:
            log.msg('entry found', uuid=entry.uuid, path=entry.path)
            return dict(identity=entry.username, password=entry.password, custom_properties=entry.custom_properties)
        else:
            log.msg('no entry found')
            password = getpass.getpass("Enter password for login '{}' used to access URL '{}': ".format(identity, url))
            return dict(identity=entry.username, password=password, custom_properties={})

        return None