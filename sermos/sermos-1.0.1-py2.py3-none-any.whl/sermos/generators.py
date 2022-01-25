import os
from boto3 import Session
import logging

logger = logging.getLogger(__name__)


class KeyGenerator(object):
    """ Common functions for key generators.
    """
    def __init__(self):
        super(KeyGenerator, self).__init__()
        self.hidden_files = ('.DS_Store', '.git', 'Icon', '.Dropbox')

    def get_file_key(self, file_obj):
        """ Required for each specific generator - how to extract key
        """
        return file_obj

    def get_file_name(self, file_obj):
        """ Required for each specific generator - how to extract file name
        """
        return file_obj

    def get_file_size(self, base_path, file_obj):
        """ Required for each specific generator - how to find file size (BYTES)
        """
        return 0

    def get_final_path(self, base_path, file_name, return_full_path):
        """ Required for each specific generator - create final file path that
            is added to list.
        """
        if return_full_path:
            return os.path.normpath(base_path + '/' + file_name)

        return file_name

    def list_iterator(self, all_files, base_path, limit=None, offset=None,
                      size_limit=None, return_full_path=True,
                      skip_common_hidden=True):
        """ accept vars from everywhere to handle offset/limit/size logic
        """
        filtered_files = []
        try:
            # Compile list of all files within limit/offset if those exist
            idx = -1
            listed_files = 0
            offset_reached = False
            for f in all_files:
                this_key = self.get_file_key(f)
                this_filename = self.get_file_name(f)

                if skip_common_hidden and this_filename in self.hidden_files:
                    continue

                idx += 1
                if offset and idx >= int(offset):
                    offset_reached = True

                if (limit and listed_files >= int(limit))\
                        or (offset and not offset_reached):
                    continue

                # Verify filesize. Having some issues with large PDFs (process
                # simply killed). So allow option of skipping files above certain
                # size in megabytes.
                if size_limit is not None:
                    size_in_bytes = self.get_file_size(base_path, f)
                    if size_in_bytes > size_limit:
                        continue

                filtered_files.append(
                    self.get_final_path(base_path, this_key, return_full_path)
                )
                listed_files += 1
        except Exception as e:
            logger.error("Unable to list objects: {0}".format(e))

        return filtered_files


class S3KeyGenerator(KeyGenerator):
    """ Produce a list of object keys from S3.
    """
    def __init__(self, aws_access_key_id, aws_secret_access_key,
                 aws_region='us-east-1'):
        super(S3KeyGenerator, self).__init__()

        session = Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        self.s3 = session.client('s3')

    def get_file_key(self, file_obj):
        """ Get file key from s3 object """
        return file_obj.get('Key', None)

    def get_file_name(self, file_obj):
        """ Get file name from s3 object """
        if file_obj is not None:
            key = file_obj.get('Key', None)
            if key is not None:
                return key.split('/')[-1]
        return None

    def get_file_size(self, base_path, file_obj):
        """ Return file size of s3 object """
        return file_obj.get('Size', 0)

    # All files in bucket
    # Range of files with an offset
    def list_files(self, bucket, folder='', limit=None, offset=None,
                   size_limit=None, return_full_path=True,
                   skip_common_hidden=True):
        """ Lists files inside an S3 bucket+folder

            Note: This does not guarantee any sort of order. Boto+S3 does not
            provide an interface for sorting results, so that would need
            to happen in memory.

            limit will include a maximum of 'limit' values
            offset will start including values only after 'offset' keys
            size_limit will not include files over a specific size (in bytes)
            skip_common_hidden will exclude common hidden files
            return_full_path will include 'bucket/' in key.
        """
        files = []

        try:
            file_data = self.s3.list_objects_v2(
                Bucket=bucket, Delimiter='/', Prefix=folder)
            files = self.list_iterator(
                file_data['Contents'],
                bucket,
                limit=limit,
                offset=offset,
                size_limit=size_limit,
                return_full_path=return_full_path,
                skip_common_hidden=skip_common_hidden
            )

        except Exception as e:
            logger.error("Unable to list objects: {0}".format(e))
        return files


class LocalKeyGenerator(KeyGenerator):
    """ Generic generator to produce a list of file names from filesystem.
    """
    def __init__(self):
        super(LocalKeyGenerator, self).__init__()

    def get_file_key(self, file_obj):
        """ Get file key from local object """
        return file_obj

    def get_file_name(self, file_obj):
        """ Get file name from local object """
        return file_obj

    def get_file_size(self, base_path, file_obj):
        """ Get file size from local object """
        full_path = os.path.normpath(base_path + '/' + file_obj)
        try:
            return os.stat(full_path).st_size
        except Exception as e:
            logger.error("File {0} not found ...".format(full_path))
        return 0

    def list_files(self, folder_path, limit=None, offset=None,
                   size_limit=None, return_full_path=True,
                   skip_common_hidden=True):
        """ Lists all file names inside a path.

            skip_common_hidden will exclude common hidden files
            return_full_path will include path in addition to filename
        """
        files = []
        try:
            file_data = os.listdir(folder_path)
            files = self.list_iterator(
                file_data,
                folder_path,
                limit=limit,
                offset=offset,
                size_limit=size_limit,
                return_full_path=return_full_path,
                skip_common_hidden=skip_common_hidden
            )

        except Exception as e:
            logger.error("Unable to list objects: {0}".format(e))
        return files
