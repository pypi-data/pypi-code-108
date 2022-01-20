from autoactive.archive.dataobject import Dataobject

from dataclasses import dataclass


@dataclass(init=False)
class Folder(Dataobject):
    """ Class used for creating a folder in the Dataobject """

    def __init__(self):
        super().__init__()
        self.meta.type: str = "no.sintef.folder"
        self.meta.version: int = 1

    def from_serializable(self, _):
        """ Overwrites the implementation in Dataobject,
            should not be used """

        assert False, "Not implemented"

    @classmethod
    def from_dict(cls, dict_, archive_reader):
        """ Class constructor used when object is
            constructed from file

        :arg
            dict_ (dict): Metadata used for creating the Folder object

            archive_reader (ArchiveReader): Object used for reading data
            from aaz file

        :returns
            obj (Folder): Folder object
        """

        obj = Folder.__new__(cls)
        super().__init__(obj)
        obj.to_natives(dict_, archive_reader)
        return obj
