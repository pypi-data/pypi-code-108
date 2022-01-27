import boto3


class S3WorkFileManager:
    """
    Manages volume manifest tool work files
    """

    _hostname: str

    # noinspection PyBroadException
    @staticmethod
    def me_instance() -> str:
        """
        Returns a string representing an instance id
        :return:
        """

        instance_id: str = "unknown instance"
        try:
            import requests
            response = requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout=2)
            instance_id = response.text
        except Exception:
            from os import getpid
            import platform
            import datetime

            # Build the destination name
            now: datetime = datetime.datetime.now()

            hostname: str = platform.node()
            pid: int = getpid()
            instance_id = f"{now.year}-{now.month}-{now.day}_{now.hour}_{now.minute}_{now.second}-{hostname}.{pid}"

        return instance_id

    def s3_move(self, src_object: str, dest_object: str, src_folder, dest_folder):
        """
        Moves a source list from one "folder" to another in S3,
        The bucket is found in the constructor

        :param src_object:  source object name
        :param dest_object: destination
        :param src_folder: source path under bucket
        :param dest_folder: destination path

        Throws on error
        """

        src_object = f'{src_folder}{src_object}'
        dest_object = f'{dest_folder}{dest_object}'

        self.s3.Object(self._bucket_name, dest_object).copy_from(
            CopySource={'Bucket': self._bucket_name, 'Key': src_object})
        self.s3.Object(self._bucket_name, src_object).delete()

    def s3_move_list(self, src_list: [], dest_list: [], src_path: str, dest_path: str):
        for src, dest in zip(src_list, dest_list):
            self.s3_move(src, dest, src_path, dest_path)

    def local_name_work_file(self, file_name: str):
        """
        Generate a name unique to this instance
        :param file_name: Name to be transformed
        :return: file_name-instance-id
        """
        return f'{file_name}-{self._hostname}'

    def mark_underway(self, object_list: [], dest_name_list: []):
        """
        Moves a set of files from the instance's to do into underway.
        Caller can use local_name_work_file() to rename
        :param object_list:
        :param dest_name_list:
        :return:
        """
        self.s3_move_list(object_list, dest_name_list, self._src_folder, self._underway_folder)

    def mark_done(self, object_list: [], dest_name_list: []):
        """
        Moves a set of files from the instance's underway folder to a done folder
        :param object_list:
        :param dest_name_list:
        :return:
        """
        self.s3_move_list(object_list, dest_name_list, self._underway_folder, self._done_folder, )

    def __init__(self, bucket_name: str, src_folder: str, underway_folder: str, done_folder: str):
        """
        Initializer:
        :param bucket_name: scope of all operations
        :param src_folder: location of work list
        :param underway_folder: folder inside bucket where in progress files go
        :param done_folder:  folder inside bucket where completed files go
        """
        self._bucket_name = bucket_name
        self._hostname = self.me_instance()
        self._src_folder = src_folder
        self._underway_folder = underway_folder
        self._done_folder = done_folder

        self.s3 = boto3.resource('s3')
