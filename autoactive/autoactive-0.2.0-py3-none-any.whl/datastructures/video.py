from autoactive.archive.fileobject import Fileobject
from autoactive.datastructures.meta import Meta
from autoactive.datastructures.user import User


class Video(Fileobject):

    """ Class containing information about a video file """

    def __init__(self):
        super().__init__()
        self.meta.type = "no.sintef.video"
        self.meta.version = 1
        self.meta.time_scale = 1
        self.meta.start_time = 0
        self.meta.is_world_clock = False

    def from_serializable(self, _):
        """ Overwrites the implementation in Dataobject,
            should not read video into memory when data
            is read from aaz file, as they may be very large
            and not always necessary
        """
        return self

    @classmethod
    def from_dict(cls, dict_, archive_reader):
        """ Class constructor used when object is
            constructed from file

        :arg
            dict_ (dict): Metadata used for creating the Video object

            archive_reader (ArchiveReader): Object used for reading data
            from aaz file

        :returns
            obj (Session): Pythonic representation of a session
        """

        obj = Video.__new__(cls)
        obj._meta = Meta()
        obj._user = User()
        obj.to_natives(dict_, archive_reader)
        return obj

    def copy_video_to_file(self, archive_reader, fname):
        """ Copies video to file

        :arg
            archive_reader (ArchiveReader): Object used for reading data
            from aaz file

            fname (Path): Path for where to copy video
        """
        
        assert hasattr(self.meta, "attachments"), "No attachment exist for obj"
        assert (
            len(self.meta.attachments) == 1
        ), "There must be exactly one video in one object"
        for elem_name in self.meta.attachments:
            archive_reader.copy_content_to_file(elem_name, fname)
