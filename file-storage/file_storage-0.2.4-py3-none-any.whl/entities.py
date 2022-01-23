"""Сущности для работы с хранилищами"""
from dataclasses import dataclass

class Type:
    """Класс типа хранилища"""
    DISK = "disk"
    FTP = "ftp"
    S3 = "s3"

@dataclass
class Key:
    """Класс доступа к хранилищу"""
    url: str
    username: str
    password: str

@dataclass
class Resource:
    """Класс доступа к ресурсу хранилища"""
    type: Type
    key: Key
    path: str