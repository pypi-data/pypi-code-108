from autoactive.archive.fileobject import Fileobject

from dataclasses import dataclass


@dataclass
class Source(Fileobject):
    """ Object representing the source """

    def __init__(self):
        super().__init__()
        self.meta.type: str = "no.sintef.source"
        self.meta.version: int = 1
        self.user.language: str = "PYTHON"

    def from_serializable(self, _):
        return self

    @classmethod
    def from_dict(cls, dict_, archive_reader):
        """ Class constructor used when object is
            constructed from file

        :arg
            dict_ (dict): Metadata used for creating the Source object

            archive_reader (ArchiveReader): Object used for reading data
            from aaz file

        :returns
            obj (Session): Pythonic representation of source information
        """

        obj = Source.__new__(cls)
        super().__init__(obj)
        obj.to_natives(dict_, archive_reader)
        return obj
