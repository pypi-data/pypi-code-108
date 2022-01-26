from urllib.parse import urlparse

import psycopg2  # type: ignore

from unipipeline.waiting.uni_wating import UniWaiting


class UniPostgresWaiting(UniWaiting):

    def get_connection_uri(self) -> str:
        raise NotImplementedError(f'method get_connection_uri was not specified for {type(self).__name__}')

    def try_to_connect(self) -> None:
        parsed_db_uri = urlparse(self.get_connection_uri())
        psycopg2.connect(
            dbname=parsed_db_uri.path.strip('/'),
            user=parsed_db_uri.username,
            password=parsed_db_uri.password,
            host=parsed_db_uri.hostname,
            port=parsed_db_uri.port,
        )
