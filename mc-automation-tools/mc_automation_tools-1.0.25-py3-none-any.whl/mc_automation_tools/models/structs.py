"""
This module provide common struct & class
"""
import enum


class S3Provider:
    """This class provide s3 credential """
    def __init__(self, entrypoint_url, access_key, secret_key, bucket_name=None):
        self.s3_entrypoint_url = entrypoint_url
        self.s3_access_key = access_key
        self.s3_secret_key = secret_key
        self.s3_bucket_name = bucket_name

    def get_entrypoint_url(self):
        return self.s3_entrypoint_url

    def get_access_key(self):
        return self.s3_access_key

    def get_secret_key(self):
        return self.s3_secret_key

    def get_bucket_name(self):
        return self.s3_bucket_name


class StorageProvider:
    """This class provide gathered access to core's storage credential """

    def __init__(self,
                 source_data_provider=None,
                 tiles_provider=None,
                 fs_provider=None,
                 s3_credential=None,
                 pvc_handler_url=None):
        self.__source_data_provider = source_data_provider
        self.__tiles_provider = tiles_provider
        self.s3_credential = s3_credential
        self.__pvc_handler_url = pvc_handler_url
        self.__fs_provider = fs_provider

    def get_source_data_provider(self):
        return self.__source_data_provider

    def get_tiles_provider(self):
        return self.__tiles_provider

    def get_s3_credential(self):
        return self.s3_credential

    def get_pvc_url(self):
        return self.__pvc_handler_url

    def fs_provider(self):
        return self.__fs_provider


class FSProvider:
    """This class provide relevant variables for fs mode """

    def __init__(self,
                 is_fs=False,
                 root_dir_path=None,
                 src_relative_path=None,
                 dst_relative_path=None):
        self.__is_fs = is_fs
        self.__root_dir_path = root_dir_path
        self.__src_relative_path = src_relative_path
        self.__dst_relative_path = dst_relative_path

    def is_fs(self):
        return self.__is_fs

    def get_root_dir_path(self):
        return self.__root_dir_path

    def get_src_relative_path(self):
        return self.__src_relative_pathgit

    def get_dst_relative_path(self):
        return self.__dst_relative_path


class ResponseCode(enum.Enum):
    """
    Types of server responses
    """
    Ok = 200  # server return ok status
    ChangeOk = 201  # server was return ok for changing
    NoJob = 204  # No job
    ValidationErrors = 400  # bad request
    StatusNotFound = 404  # status\es not found on db
    DuplicatedError = 409  # in case of requesting package with same name already exists
    GetwayTimeOut = 504  # some server didn't respond
    ServerError = 500  # problem with error


class JobStatus(enum.Enum):
    """
    Types of job statuses
    """
    Completed = 'Completed'
    Failed = 'Failed'
    InProgress = 'In-Progress'
    Pending = 'Pending'


class MapProtocolType(enum.Enum):
    """
    Types of orthophoto access protocol statuses
    """
    WMS = 'WMS'
    WMTS = 'WMTS'
    WMTS_LAYER = 'WMTS_LAYER'


class tile_storage_provider(enum.Enum):
    S3 = "S3"
    FS = "FS"
    PV = "PV"
