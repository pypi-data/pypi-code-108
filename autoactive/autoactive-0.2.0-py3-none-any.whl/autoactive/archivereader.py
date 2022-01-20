from autoactive.autoactive.session import Session
from autoactive.autoactive.folder import Folder
from autoactive.autoactive.datatable import Datatable
from autoactive.datastructures.video import Video
from autoactive.autoactive.source import Source

from dataclasses import dataclass
import json
import zipfile as zp
import pyarrow.parquet as pq
import io


@dataclass(frozen=True)
class ArchiveOverview:
    """Stores session information

    :arg
        id (str): Session id

        name (str): Session name
    """

    id: str = None
    name: str = None


class ArchiveReader:
    """Class for reading aaz file

    :arg
        path (Path): Path to aaz file
    """

    def __init__(self, path):
        self.path = path
        self._file = zp.ZipFile(path, "r", allowZip64=True)
        self.overview = self.get_overview()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _open(self, path):

        """Method that accesses a member
            of the archive as a binary file-like object

        :arg
            path (str): Can be either the name of a file
            within the archive or a ZipInfo object

        :returns
            original (zipfile): Accessible member in the
            zipfile

        """

        original = self._file.open(path, "r")
        return original

    def close(self):
        self._file.close()

    def read_table(self, elem_name):
        """Method for reading parquet tables

        :arg
            elem_name (str): The complete path of element inside
            aaz file

        :returns
            df (DataFrame): Returns the parquet table as a pandas dataframe
        """

        buffer = io.BytesIO()
        with self._open(elem_name) as file:
            buffer.write(file.read())
        df = pq.read_table(buffer).to_pandas()
        return df

    def list_ids(self):
        """Gets a list of session ids

        :returns
            (list): Session ids
        """

        fnames = self._file.namelist()
        session_names = [fname.split("/")[0] for fname in fnames]
        return list(set(session_names))

    def get_metadata_name_from_id(self, id):
        """Gets the name of the json file in session

        :arg:
            id (str): Session id

        returns:
            elem_name (str): The complete path to json file inside
            aaz file
        """

        elem_names = self._file.namelist()
        elem_name = [ename for ename in elem_names if id in ename and ".json" in ename]
        assert len(elem_name) == 1
        elem_name = elem_name[0]
        return elem_name

    def read_session_name_from_metadata(self, elem_name):
        """Reads session name

        :arg
            elem_name (str): Path to json file

        :returns
            name (str): Session name
        """

        name = self.read_metadata(elem_name)["user"]["name"]
        return name

    def read_metadata(self, elem_name):
        """Reads metadata from file

        :arg
            elem_name (str): Path to json file

        :returns
            metadata (dict): The deserialized json file
        """

        with self._open(elem_name) as file:
            metadata = json.load(file)
        return metadata

    def get_session_name_from_id(self, id):
        """Gets the name of the session

        :arg
            id (str): Session id

        :returns
            session_name (str): Session name
        """

        elem_name = self.get_metadata_name_from_id(id)
        session_name = self.read_session_name_from_metadata(elem_name)
        return session_name

    def get_overview(self):
        """Gets sessions in aaz file

        :returns
            archive_overview (list[ArchiveOverview]): Overview of
            sessions in aaz file
        """

        archive_overview = list()
        ids = self.list_ids()
        for id in ids:
            name = self.get_session_name_from_id(id)
            archive_overview.append(ArchiveOverview(id, name))
        return archive_overview

    def open_session(self, id):
        """Open session in aaz file

        :arg
            id (str): Session id

        :returns
            s (session): A pythonic representation of the
            aaz file
        """

        metadata_elem_name = self.get_metadata_name_from_id(id)
        metadata = self.read_metadata(metadata_elem_name)
        self.open_session_id = id
        s = Session.from_dict(metadata, self)
        return s

    def json_type_to_native(self, type, json):
        """Converts data from dict to native python object

        :arg
            type (str): native python type

            json (dict): data

        returns:
             (Dataobject): Pythonic representation of data
        """

        if type == "no.sintef.folder":
            return Folder.from_dict(json, self)
        elif type == "no.sintef.table":
            return Datatable.from_dict(json, self)
        elif type == "no.sintef.video":
            return Video.from_dict(json, self)
        elif type == "no.sintef.source":
            return Source.from_dict(json, self)
        else:
            assert False, f"There does not exist a native type for {type}"

    def copy_content_to_file(self, elem_name, fname):
        """Copies content from archive to file

        :arg
            elem_name (str): The complete path to file
            inside aaz file

            fname (Path): directory for where to copy
            the file
        """

        elem_name = f"{self.open_session_id}{elem_name}"
        self._file.extract(elem_name, fname)
