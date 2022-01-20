from typing import Optional
import os
from cryptography import x509
from .serializers import serializer
from . import key_value_store, backends, serializers, models

class SftpStorage(key_value_store.KeyValueStore):
    def __init__(
        self,
        host: str,
        port: int = 5432,
        dbname: str = "postgres",
        sslmode: str = "require",
        user: Optional[str] = None,
        folder: str = ".",
    ):
        user = user if user is not None else get_cert_username()
        self.backend = backends.Sftp(user, host, port, dbname, sslmode, folder = folder)
        super().__init__()

    def list(self, path: str = ".") -> models.Listing:
        return self.backend.list(path)

class SftpDataStorage(SftpStorage):
    def __init__(
        self,
        host: str,
        port: int = 5432,
        dbname: str = "postgres",
        sslmode: str = "require",
        user: Optional[str] = None,
        folder: str = ".",
        serializer: Optional[serializer.Serializer] = None,
    ):
        self.serializer = serializer if serializer is not None else serializers.Parquet()
        super().__init__(host, port, dbname, sslmode = sslmode, user = user, folder = folder)


class SftpObjectStorage(SftpStorage):
    def __init__(
        self,
        host: str,
        port: int = 5432,
        dbname: str = "postgres",
        sslmode: str = "require",
        user: Optional[str] = None,
        folder: str = ".",
    ):
        self.serializer = serializers.Pickle()
        super().__init__(host, port, dbname, sslmode = sslmode, user = user, folder = folder)

