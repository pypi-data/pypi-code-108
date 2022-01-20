from autoactive.datastructures.meta import Meta
from autoactive.datastructures.user import User

from dataclasses import dataclass


@dataclass(init=False)
class Dataobject:
    """ Parent class for all dataobjects """

    def __init__(self):
        self._meta: Meta = Meta()
        self._user: User = User()

    @property
    def meta(self):
        return self._meta

    @property
    def user(self):
        return self._user

    def __setattr__(self, key, value):
        if isinstance(value, Dataobject):
            self.user.__dict__[key] = value
        else:
            self.__dict__[key] = value

    def __getattr__(self, item):
        if item not in self.__dict__.keys():
            return self.user.__dict__[item]
        else:
            return self.__dict__[item]

    def to_serializable(self, **kwargs):
        """ Method which transforms the dataobject to a
        serializable object

        :arg
            **kwargs (dict): Dictionary containing the archiveWriter,
            uuid and the parent key

        :returns
            dict (dict): Representing the dataobject as a dictionary
        """

        meta = self.meta.__dict__
        user = self.user.__dict__

        return {"meta": meta, "user": user}

    def replace_natives(self, **kwargs):
        """ Transforms the nested python objects to nested
            serializable objects

        :arg
            **kwargs (dict): Dictionary containing the archiveWriter
            uuid and the parent key

        :returns
            ser_obj (serializable): Representing the dataobject as
            a serializable object
        """

        ser_obj = self.to_serializable(**kwargs)
        for key, value in ser_obj["user"].items():
            kwargs["parent_key"] = key
            if isinstance(value, Dataobject):
                ser_obj["user"][key] = value.replace_natives(**kwargs)
        return ser_obj

    @classmethod
    def from_dict(cls, dict_, archive_reader):
        """ Constructor when transforming nested dictionary
            to native python object

        :arg
            dict_ (dict): Metadata used to create the dataobject

            archive_reader (ArchiveReader): Object used for reading
            from aaz file

        :returns
            obj (Dataobject): Pythonic representation of the dataobject.
        """

        obj = Dataobject.__new__(cls)
        obj._meta = Meta()
        obj._user = User()
        obj.to_natives(obj, dict_, archive_reader)
        return obj

    def to_natives(obj, dict_, archive_reader):
        """ Transforms the nested dictionary to native python
            object

        :arg
            dict_ (dict): Metadata used to create the dataobject.

            archive_reader (ArchiveReader): Object used for reading
            from aaz file

        :returns
            obj (Dataobject): Pythonic representation of the dataobject
        """

        for k, v in dict_["meta"].items():
            obj.meta.__setattr__(k, v)
        for k, v in dict_["user"].items():
            if isinstance(v, dict):
                if "meta" and "user" in v.keys():
                    v = archive_reader.json_type_to_native(v["meta"]["type"], v)
            obj.user.__setattr__(k, v)
        if hasattr(obj.meta, "attachments"):
            obj.from_serializable(archive_reader)
        return obj
