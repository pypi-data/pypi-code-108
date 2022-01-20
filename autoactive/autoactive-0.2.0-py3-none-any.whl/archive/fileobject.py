from autoactive.archive.dataobject import Dataobject
from autoactive.autoactive.folder import Folder
from autoactive.datastructures.fileinfo import Fileinfo

from dataclasses import dataclass
from pathlib import Path


@dataclass(init=False)
class Fileobject(Dataobject):
    """ Parent class for all fileobjects """

    def __init__(self):
        super().__init__()
        self.type: str = None
        self.version: int = None
        self.meta.write_type: str = None

    def add_content_from_file_to_archive(self, fname):
        """ Method saving content from file to the aaz file.

        args:
            fname (Path): The full path of the file

        Returns:
            self (Source): Object containing information
            about data source in aaz file
        """

        self.user.file_name_full = str(fname)
        file_details = Fileinfo(fname)
        self.user.file_details = self.dataclass_to_folder(file_details)
        self.meta.write_type = "from_file"
        return self

    def load_content_from_archive_to_file(self, archive_reader, fname):
        """ Copies video to file

        :arg
            archive_reader (ArchiveReader): Object used for reading data
            from aaz file

            fname (Path): Path for where to copy content
        """

        assert hasattr(self.meta, "attachments"), "No attachment exist for obj"
        assert (
            len(self.meta.attachments) == 1
        ), "There must be exactly one attachment in one object"
        for elem_name in self.meta.attachments:
            archive_reader.copy_content_to_file(elem_name, fname)

    def dataclass_to_folder(self, data) -> Folder:
        """ Method which transforms dictionary to folder

        :arg
            data (Datatable): Data to be transformed

        :returns
            folder (Folder): Folder object
        """

        folder = Folder()
        folder.user.__dict__ = data.__dict__
        return folder

    def to_serializable(self, **kwargs):
        """ Method which transforms the dataobject to a
        serializable object

        :args:
            **kwargs (dict): Dictionary containing the archiveWriter,
            uuid and the parent key

        :returns
            dict (dict): Representing the Fileobject as a dictionary
        """

        elem_path = (
            f"{self.user.file_details.user.folder}\\{self.user.file_details.user.name}"
        )
        path = f"{kwargs['uuid']}/{kwargs['parent_key']}/{self.user.file_details.user.name}"
        self.meta.attachments = [
            f"/{kwargs['parent_key']}/{self.user.file_details.user.name}"
        ]
        kwargs["archive_writer"].copy_content_from_file(elem_path, path)
        meta = self.meta.__dict__
        user = self.user.__dict__
        return {"meta": meta, "user": user}
