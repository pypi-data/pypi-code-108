# Copyright 2021 Cegal AS
# All rights reserved

import sqlite3
from os import makedirs, path

from cegal.keystone_auth import logger as logger


class _TokenDb:
    def __init__(self, db_location, client_id) -> None:
        self._db_location = db_location
        self._client_id = client_id
        makedirs(path.dirname(self._db_location), exist_ok=True)
        self._create_table_if_not_exists()

    def get_token_from_db(self):
        logger.debug(f"Getting token from {self._db_location}")
        conn = sqlite3.connect(f"file:{self._db_location}?mode=ro", uri=True)
        curs = conn.cursor()
        curs.execute(
            "SELECT * FROM client_tokens WHERE client_id=?", (self._client_id,)
        )
        token = curs.fetchone()
        conn.close()
        return token

    def get_client_ids(self):
        logger.debug(f"Retrieving all stored token client_ids")
        conn = sqlite3.connect(f"file:{self._db_location}?mode=ro", uri=True)
        curs = conn.cursor()
        curs.execute("SELECT client_id FROM client_tokens")
        ids = curs.fetchall()
        conn.close()
        return [x[0] for x in ids]

    def store_token_in_db(self, id_token, access_token, refresh_token):
        conn = sqlite3.connect(f"file:{self._db_location}?mode=rw", uri=True)
        curs = conn.cursor()
        # Alternative SQL to ON CONFLICT as not suppported on older versions
        curs.execute(
            "UPDATE client_tokens SET id_token=?, access_token=?, refresh_token=? WHERE client_id=?",
            (
                id_token,
                access_token,
                refresh_token,
                self._client_id,
            ),
        )
        curs.execute(
            "INSERT OR IGNORE INTO client_tokens(client_id, id_token, access_token, refresh_token) VALUES (?, ?, ?, ?)",
            (
                self._client_id,
                id_token,
                access_token,
                refresh_token,
            ),
        )
        conn.commit()
        conn.close()

    def delete_token_from_db(self):
        conn = sqlite3.connect(f"file:{self._db_location}?mode=rw", uri=True)
        curs = conn.cursor()
        curs.execute(
            "DELETE FROM client_tokens WHERE client_id = ?", (self._client_id,)
        )
        conn.commit()
        conn.close()

    def _create_table_if_not_exists(self):
        logger.debug(f"Creating {self._db_location} client_tokens table if necessary")
        conn = sqlite3.connect(f"file:{self._db_location}?mode=rwc", uri=True)
        curs = conn.cursor()
        curs.execute(
            "CREATE TABLE IF NOT EXISTS client_tokens(client_id TEXT PRIMARY KEY, id_token TEXT, access_token TEXT, refresh_token TEXT)"
        )
        conn.commit()
        conn.close()
