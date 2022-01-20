import os
import sqlite3

from tasq_cli.utils import get_config_directory


class UploadsDatabase:
    def __init__(self):
        self._connection = sqlite3.connect(os.path.join(get_config_directory(), 'uploads_v002DEV.sqlite3'))
        self._connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self._connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY,
            bucket TEXT NOT NULL,
            dataset_name TEXT NOT NULL,
            file_name TEXT NOT NULL,
            object_name TEXT NOT NULL,
            md5_hash TEXT NOT NULL,
            url TEXT NOT NULL,
            cdn_url TEXT NOT NULL
        )''')
        self._connection.commit()

    def close(self):
        self._connection.close()

    def insert_upload(self, bucket, dataset_name, file_name, object_name, md5_hash, url, cdn_url):
        if not self.get_upload(dataset_name, md5_hash):
            cursor = self._connection.cursor()
            cursor.execute(
                "INSERT INTO uploads (bucket, dataset_name, file_name, object_name, md5_hash, url, cdn_url) "
                "VALUES (?,?,?,?,?,?,?)",
                (bucket, dataset_name, file_name, object_name, md5_hash, url, cdn_url)
            )
            self._connection.commit()

    def get_upload(self, dataset_name, md5_hash):
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT bucket, dataset_name, file_name, object_name, md5_hash, url, cdn_url FROM uploads WHERE dataset_name=? AND md5_hash=?",
            (dataset_name, md5_hash,)
        )
        return cursor.fetchone()

    def get_uploaded_files_by_dataset_name(self, dataset_name):
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT file_name, cdn_url FROM uploads WHERE dataset_name=?",
            (dataset_name,)
        )
        return cursor.fetchall()

    def get_dataset_name_by_filename(self, file_name):
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT dataset_name FROM uploads WHERE file_name=?",
            (file_name,)
        )
        return cursor.fetchone()
