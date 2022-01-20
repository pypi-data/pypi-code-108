from autoactive.archive.dataobject import Dataobject
from autoactive.datastructures.meta import Meta
from autoactive.datastructures.user import User

from dataclasses import dataclass
from functools import singledispatch
import numpy as np
import pandas as pd
from uuid import uuid4


@dataclass
class Data:
    """ Class for storing 1d sensor data """

    data = None
    unit = None


@dataclass(init=False)
class Datatable(Dataobject):
    """ Class for storing 1d sensor data refrencing the same time vector """

    @property
    def column_names(self):
        return [
            key
            for (key, value) in self.user.__dict__.items()
            if isinstance(value, Data)
        ]

    @property
    def dtypes(self):
        return [d.data.dtype for d in self.user.__dict__.values()]

    @property
    def units(self):
        for d in self.user.__dict__.values():
            a = d.unit
        return [d.unit for d in self.user.__dict__.values()]

    @property
    def data(self):
        return [d.data for d in self.user.__dict__.values() if isinstance(d, Data)]

    @property
    def as_dict(self):
        return {key: value for (key, value) in zip(self.column_names, self.data)}

    @property
    def as_dataframe(self):
        return pd.DataFrame(self.as_dict)

    def __init__(self):
        super().__init__()
        self.meta.type = "no.sintef.table"
        self.meta.version = 1

    def __setattr__(self, name, value):
        _setattr(value, name, self)

    def __getattr__(self, item):
        return self.user.__dict__[item]

    def to_serializable(self, **kwargs):
        """ Method which transforms the table object to a
            serializable object

        :arg
            **kwargs (dict): Dictionary containing the archiveWriter
            uuid and the parent key

        :returns
            dict (dict): Metadata for the table object
        """

        assert "time" in self.column_names, "No time column found"
        assert self.time.unit != None, "The time column must have a unit"
        file_ending = uuid4()
        path = f"{str(kwargs['uuid'])}/data/{str(kwargs['parent_key'])}.{file_ending}"
        self.meta.attachments = [f"/data/{str(kwargs['parent_key'])}.{file_ending}"]
        self.meta.units = self.units
        self.meta.is_world_clock = False
        kwargs["archive_writer"].write_table(path, self)
        return {"user": dict(), "meta": self.meta.__dict__}

    def from_serializable(self, archive_reader):
        """ Method which transforms the serializable object to a
        table object

        :arg
            archive_reader (ArchiveReader): Object for reading data
            from aaz file

        :returns
            self (Datatable): Object storing 1d sensor data
            referencing the same timeline
        """

        for file in self.meta.attachments:
            df = archive_reader.read_table(archive_reader.open_session_id + file)
            for i, column in enumerate(df.columns):
                self.__setattr__(column, df[column].values)
                self.user.__dict__[column].unit = self.meta.units[i]
        delattr(self.meta, "units")
        delattr(self.meta, "attachments")
        return self

    @classmethod
    def from_dict(cls, dict_, archive_reader):
        """ Class constructor used when object is
            constructed from file

        :arg
            dict_ (dict): Metadata used for creating the Datatable object

            archive_reader (ArchiveReader): Object for reading data
            from aaz file

        :returns
            obj (Datatable): Object storing 1d sensor data
            referencing the same timeline
        """

        obj = Datatable.__new__(cls)
        super().__init__(obj)
        obj.to_natives(dict_, archive_reader)
        return obj


@singledispatch
def _setattr(value, name, self) -> None:
    """ Helper methods for __setattr__ in Datatable class, so user
        can use . notation without having to also call meta or user.
        If value is of type array first method is used
        (@_setattr.register(np.ndarray)), if value is of type Meta
        or user, the second method is called. For any other type a
        error is thrown

    :arg
        value(np.ndarray/Meta/user): Value to be set

        name (str): Name of attribute

        self (Datatable): Object storing 1d sensor data
    """

    assert False, "Type not implemented"


@_setattr.register(np.ndarray)
def _(value, name, self: Datatable) -> None:
    d = Data()
    d.data = value
    self.user.__dict__[name] = d


@_setattr.register(Meta)
@_setattr.register(User)
def _(value, name, self: Datatable) -> None:
    self.__dict__[name] = value
