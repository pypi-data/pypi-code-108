from datetime import date, datetime, timedelta

import click

from sotooncli import requests
from sotooncli.settings import APP_DIR
from sotooncli.utils import delete_file, get_strerror, read_json, write_to_json


class CacheUtils:
    _instance = None
    DATE_KEY = "date"
    DATA_KEY = "result"
    ETAG_KEY = "etag"

    def __new__(cls, use_cache=True, days=1):
        if cls._instance is None:
            cls._instance = super(CacheUtils, cls).__new__(cls)
            cls._instance.path = f"{APP_DIR}/cache.json"
            cls._instance.duration = timedelta(days=days)
            cls._instance.data = None
            cls._instance.date = None
            cls._instance.use_cache = use_cache
            cls._instance.etag = None
        return cls._instance

    def read_cache(self):
        if not self._instance.use_cache:
            return False
        try:
            data = read_json(self.path)
            self._instance.data = data[self.DATA_KEY]
            self._instance.etag = data[self.ETAG_KEY]
            self._instance.date = datetime.fromisoformat(data[self.DATE_KEY]).date()
            return True
        except KeyError:
            click.echo("Warning: Cache file is invalid")
        except FileNotFoundError:
            return False
        except Exception as e:
            click.echo(f"Warning: could not read cache: {get_strerror(e)}")
        return False

    def update_cache(self):
        d, e = requests.get_metadata(etag=self._instance.etag)
        if d is not None:
            self._instance.data = d
            self._instance.etag = e
        self._instance.date = date.today()
        if not self._instance.use_cache:
            return
        cache = {
            self.ETAG_KEY: self._instance.etag,
            self.DATA_KEY: self._instance.data,
            self.DATE_KEY: self._instance.date.isoformat(),
        }
        write_to_json(path=self._instance.path, value=cache)

    def has_expired(self):
        if self._instance.date + self._instance.duration <= date.today():
            return True
        return False

    def get_cache(self):
        successful = self.read_cache()
        if successful and self.has_expired():
            successful = False
        if not successful:
            self.update_cache()
        return self._instance.data

    def remove_cache(self):
        try:
            delete_file(self._instance.path)
        except FileNotFoundError:
            return
        except Exception:
            raise click.ClickException("Could not delete cache.")
