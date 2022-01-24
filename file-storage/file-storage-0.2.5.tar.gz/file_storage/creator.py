"""Вспомогательные функции для создания Storage"""
from .entities import Type, Key

from .storage import Storage
from .ftp import FtpServer
from .s3 import S3
from .disk import Disk


def new_storage_by_type(storage_type: Type, key: Key) -> Storage:
    """new_storage_by_type создает новый Storage по ключу и типу"""
    if storage_type == Type.FTP:
        return FtpServer(key.url, key.username, key.password)
    if storage_type == Type.S3:
        return S3(key.url, key.username, key.password)
    if storage_type == Type.DISK:
        return Disk()
        
    return None