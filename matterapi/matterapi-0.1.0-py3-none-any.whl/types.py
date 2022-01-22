""" Contains some shared types for properties """
from typing import Any, BinaryIO, Optional, TextIO, Tuple, Union

from pydantic import BaseModel


class BaseConfig(BaseModel):
    class Config:
        extra = "allow"
        exclude_defaults = True
        fields = {"fields": "fields_"}


class BaseMapping(BaseConfig):
    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        return data["__root__"] if self.__custom_root_type__ else data

    def __setitem__(self, key, item):
        self.__root__[key] = item

    def __getitem__(self, key):
        return self.__root__[key]

    def __repr__(self):
        return repr(self.__root__)

    def __len__(self):
        return len(self.__root__)

    def __delitem__(self, key):
        del self.__root__[key]

    def clear(self):
        return self.__root__.clear()

    def copy(self):
        return self.__root__.copy()

    def has_key(self, k):
        return k in self.__root__

    def update(self, *args, **kwargs):
        return self.__root__.update(*args, **kwargs)

    def keys(self):
        return self.__root__.keys()

    def values(self):
        return self.__root__.values()

    def items(self):
        return self.__root__.items()

    def pop(self, *args):
        return self.__root__.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__root__, dict_)

    def __contains__(self, item):
        return item in self.__root__

    def __iter__(self):
        return iter(self.__root__)

    def __unicode__(self):
        return str(repr(self.__root__))


class BaseArray(BaseConfig):
    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        return data["__root__"] if self.__custom_root_type__ else data

    def __setitem__(self, key, item):
        self.__root__[key] = item

    def __getitem__(self, key):
        return self.__root__[key]

    def __repr__(self):
        return repr(self.__root__)

    def __len__(self):
        return len(self.__root__)

    def __delitem__(self, key):
        del self.__root__[key]

    def clear(self):
        return self.__root__.clear()

    def copy(self):
        return self.__root__.copy()

    def count(self, k):
        return self.__root__.count()

    def extend(self, items):
        return self.__root__.extend(items)

    def index(self, item):
        return self.__root__.index(item)

    def insert(self, *args):
        return self.__root__.insert(*args)

    def pop(self, *args):
        return self.__root__.pop(*args)

    def remove(self, *args):
        return self.__root__.remove(*args)

    def reverse(self):
        return self.__root__.reverse()

    def sort(self, *args):
        return self.__root__.sort(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__root__, dict_)

    def __contains__(self, item):
        return item in self.__root__

    def __iter__(self):
        return iter(self.__root__)

    def __unicode__(self):
        return str(repr(self.__root__))


FileJsonType = Tuple[Optional[str], Union[BinaryIO, TextIO], Optional[str]]


class FileInfo(BaseModel):
    """Contains information for file uploads"""

    payload: Union[BinaryIO, TextIO]
    file_name: Optional[str] = None
    mime_type: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def to_tuple(self) -> FileJsonType:
        """Return a tuple representation that httpx will accept for multipart/form-data"""
        return self.file_name, self.payload, self.mime_type


File = Union[FileInfo, FileJsonType, Any]


__all__ = ["BaseConfig", "File", "FileInfo"]
