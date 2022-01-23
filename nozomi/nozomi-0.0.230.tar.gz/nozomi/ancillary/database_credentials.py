"""
Nozomi
Database Credentials Module
author: hugh@blinkybeach.com
"""
from nozomi.ancillary.immutable import Immutable
from nozomi.data.codable import Codable, CodingDefinition as CD
import json
from typing import TypeVar, Type

T = TypeVar('T', bound='DatabaseCredentials')


class DatabaseCredentials(Codable):
    """Stores and disburses database connection credentials"""

    coding_map = {
        'host': CD(str),
        'secret': CD(str),
        'database_name': CD(str),
        'user': CD(str),
        'port': CD(str)
    }

    def __init__(
        self,
        host: str,
        secret: str,
        database_name: str,
        user: str,
        port: str
    ) -> None:

        credentials = (host, secret, database_name, user)
        assert False not in [isinstance(c, str) for c in credentials]
        self._host = host
        self._secret = secret
        self._database_name = database_name
        self._user = user
        self._port = port

        return

    dsn_string: str = Immutable(lambda s: s._form_dsn_string())

    host = Immutable(lambda s: s._host)
    secret = Immutable(lambda s: s._secret)
    database_name = Immutable(lambda s: s._database_name)
    user = Immutable(lambda s: s._user)
    port = Immutable(lambda s: s._port)

    def _form_dsn_string(self) -> str:
        """Return a psycopg2 compatible 'dsn' string"""
        dsn = 'host=' + self._host
        dsn += ' dbname=' + self._database_name
        dsn += ' user=' + self._user
        dsn += ' port=' + self._port
        dsn += ' password=' + self._secret
        return dsn

    def apply_to_template(
        self,
        template: str,
        other_arguments: dict = {}
    ) -> str:
        """
        Return a string after applying secret, host, user, and dbname
        parameters to a template string
        """
        return template.format(
            secret=self._secret,
            user=self._user,
            host=self._host,
            dbname=self._database_name,
            **other_arguments
        )

    @classmethod
    def from_json(cls: Type[T], json_data: str) -> T:
        assert isinstance(json_data, str)
        return cls.decode(json.loads(json_data))
