import gzip
import json
import os
from datetime import timezone, datetime
from io import BytesIO
from pathlib import Path

import boto3
from interface import Interface


# pylint: disable=no-init, duplicate-code
class BaseWriter(Interface):
    """
        Base Writer Class with methods to implement when creating your own custom writer.
        Sets out a design pattern for creating the Custom writer class.

        Namely, the following methods should be implemented:
        (1) write metadata (optional)
        (2) append page
        (3) write file
    """

    def write_metadata(self, metadata: dict):
        """
            Method that writes metadata to local filesystem.
            args:
                metadata (dict) : metadata to be written
        """
        pass

    def append_page(self, report: list):
        """
            Called by main to get data and append rows to single array object.

            args:
                report (list): report data to append
        """
        pass

    def write_file(self):
        """Called to write a file or two database in bulk or s3"""
        pass


class CustomLocalJsonWriter:
    """
        Custom JSON Writer class which writes data to local filesystem.

        Writes data into a file.json per query. The files are written to a directory tree
    """

    def __init__(
            self,
            file_name: str,
            folder_path: str,
            **kwargs
    ):
        # creates full path
        self.folder_path = folder_path
        # create file paths
        self.file_name = file_name
        # currently overwrites metadata.json each time
        self.metadata_file = kwargs.get("metadata_file", "metadata.json")
        # init data
        self.data = []
        # init path
        self.full_path = None

    @staticmethod
    def mkdir_if_not_exists(full_path: str):
        """
            Make a new directory if one doesn't exist
        """
        Path(full_path).mkdir(parents=True, exist_ok=True)

    def check_files_in_dir(self):
        """
            Return the length of files in a directory
        """
        return len(os.listdir(self.full_path))

    @staticmethod
    def timestamp_suffix():
        """builds a filename suffix from the current timestamp"""
        curr_time = datetime.now().replace(tzinfo=timezone.utc).timestamp()
        suff = str(round(curr_time, 2)).replace(".", "_")
        return suff

    @staticmethod
    def flatten_multilist(mylist: list = None):
        """Utility function to flatten google analytics report list of list of dict"""
        flat_list = []
        for sublist in mylist:
            for item in sublist:
                flat_list.append(item)
        return flat_list

    def append_page(self, report: list):
        """
            Called by main to get data and append rows to single array object.
            args:
                report (dict): report data to append
        """
        # when to write (wrapper)
        data = [r.get('data', {}).get('rows', []) for r in report]
        restructured_data = self.flatten_multilist(data)
        self.data = self.data + restructured_data


class CustomS3JsonWriter(CustomLocalJsonWriter):
    """Class Extends Basic LocalJsonWriter"""

    def __init__(
            self,
            file_name: str,
            folder_path: str,
            bucket: str,
            profile_name: str = None,
            **kwargs
    ):
        self.os_path_sep = "/"

        if profile_name is None:
            self.boto3_session = boto3.Session()
        else:
            self.boto3_session = boto3.Session(profile_name=profile_name)

        self.bucket = bucket
        """Writes a general object to s3"""
        self.s3_resource = self.boto3_session.resource('s3')

        super().__init__(file_name=file_name, folder_path=folder_path, **kwargs)

        # create directory structure if not exists
        self.full_path = self.set_full_path(folder_path)

        self.metadata_file = kwargs.get("metadata_file", "metadata.json.gz")

    @staticmethod
    def set_full_path(folder_path):
        """Set full path to write to"""
        # creates full path
        today_date = datetime.today()
        date_prefix = today_date.strftime('%Y/%m/%d')

        full_path = [date_prefix, folder_path]

        print(full_path)
        print(os.path.join(*full_path).replace('\\', '/'))
        return os.path.join(*full_path).replace('\\', '/')

    # pylint: disable=no-member,too-many-arguments
    def write_to_s3(
            self,
            json_data,
            data_path
    ):
        """
            Write report to s3 bucket
        """
        self.s3_resource.Bucket(self.bucket).put_object(
            Key=os.path.join(self.full_path, data_path).replace('\\', '/'),
            Body=json.dumps(json_data))

    def zip_write_to_s3(
            self,
            json_data,
            data_path):
        """
            Write compressed report to s3 bucket
        """

        gz_body = BytesIO()
        gz_file = gzip.GzipFile(None, 'wb', 7, gz_body)
        gz_file.write(json.dumps(json_data).encode('utf-8'))
        gz_file.close()

        self.s3_resource.Bucket(self.bucket).put_object(
            Key=os.path.join(self.full_path, data_path).replace('\\', '/'),
            ContentEncoding='gzip',
            Body=gz_body.getvalue()
        )

    def write_file(self, data: dict, compress=False):
        """
            Upload python dict into s3 bucket
            args:
                data (dict): report data to write
                compress (bool): compress data written to s3
        """

        # generate a unix timestamp suffix for file
        self.data = data
        if compress:
            self.zip_write_to_s3(self.data, self.file_name)
        else:
            self.write_to_s3(self.data, self.file_name)
        self.data = []
