"""
This is a script for the minio handler which is wrapper that connects to the object storage
and can perform certain actions.
"""
# external lib
from tqdm import tqdm
from minio import Minio
from minio.error import S3Error
# from minio.sse import SSE_C

# internal lib
from pymedquery.src.helpers import payload_transform
from pymedquery.config import config
from pymedquery.config.logger_object import Logger


class MinioHandler:
    """The MinioHandler is wrapper around Minios python client. The purpose of the
    wrapper is to make it the python client easy to use, avoid boiler plate code
    and integrate into other programs.

    Parameters
    ----------
    storage_name : str
        specify the storage you want to connect to.
    access_key : str
        the Minio username
    secret_key : str
        the Minio password for accessing
    minio_host : str
        the name of the server that the data lake is hosted on

    Attributes
    ----------
    client : type minio.object
        The `client` is the connection to minio which is needed for all operations in
        the minio_handler.
    """
    def __init__(
            self, access_key: str, secret_key: str,
            storage_name: str = 'medical_storage',
            minio_host: str = 'storage.medical-database.com'
            ):
        """__init__.

        Parameters
        ----------
        access_key : str
            access_key is the minio username for the client
        secret_key : str
            secret_key is the minio password for the client
        storage_name : str
            storage_name is the minio storage name
        minio_host : str
            minio_host where the data lake is hosted
        """
        self.STORAGE_NAME = storage_name
        self.log = Logger(__name__)
        # self.SSEC = SSE_C(config.ENC_KEY)
        try:
            self.client = Minio(
                        endpoint=minio_host,
                        access_key=access_key,
                        secret_key=secret_key,
                        secure=True
                        )
            self.log.success(f'connection to {self.STORAGE_NAME} established')
        except S3Error as e:
            self.log.error(f'Could not connect to the storage: {e}')

    def create_bucket(self, bucket_name: str):
        """Create a bucket in the Minio storage.
        Parameters
        ----------
        bucket_name: str
            Specify the name you want to call the bucket. (Be aware about Minios
            naming convetions).
        Returns
        -------
        None
        """
        if not self.client.bucket_exists(bucket_name):
            try:
                self.client.make_bucket(
                                bucket_name=bucket_name,
                                location='eu-west-1'
                                )
                self.log.success(f'created the bucket: {bucket_name}')
            except S3Error as e:
                self.log.error(
                        f'Could not create the bucket {bucket_name}: {e}',
                        )
            # try:
            #     self.log.info('encrypting the bucket')
            #     self.client.put_bucket_encryption(enc_config=config.ENCRYPT)
            # except RuntimeError:
            #     self.log.error('Could not encrypt the bucket', exc_info=True)

        else:
            self.log.info(f'The bucket {bucket_name} already exists')

    def get_buckets(self) -> dict:
        """List all the buckets that exist in the storage
        and the correspongding meta information.
        Returns
        -------
        dict
            A defaultdict is returned with the name of the buckets as keys and the
            corresponding meta information as a list value.
        """
        self.log.info(f'listing all buckets in the storage {self.STORAGE_NAME}')
        for bucket in self.client.list_buckets():
            bucket_specs = [bucket.name, bucket.creation_date]
            for key, value in zip(config.BUCKET_KEYS, bucket_specs):
                config.bucket_dict[key].append(value)
        return config.bucket_dict

    def list_blobs(self, bucket_name: str, prefix: str = None) -> dict:
        """List all the blobs in a specific bucket. The method takes either
        a string name or a list of string names and will return a dict with
        a specific blob name or all the blob names in the list and their corresponding
        meta information.
        Parameters
        ----------
        bucket_name : str
            Specify the name you want to call the bucket. (Be aware about Minios
            naming convetions).
        prefix : str
            Specify `prefix` if there is a known prefix to the blobs you want to fetch.
        Returns
        -------
        dict
            A defaultdict with the blob name/s as keys and the metainformation as list value/s.
        """
        blobs = self.client.list_objects(
                                        bucket_name=bucket_name,
                                        prefix=prefix,
                                        recursive=True
                                        )
        for blob in blobs:
            for keys, values in zip(['last_modified', 'etag', 'size'], [blob.last_modified, blob.etag, blob.size]):
                config.nested_blob_dict[blob.object_name][keys] = values

        return config.nested_blob_dict

    def delete_bucket(self, bucket_name: str):
        """The method deletes a bucket in storage.
        Parameters
        ----------
        bucket_name : str
            Specify the name you want to call the bucket. (Be aware about Minios
            naming convetions).
        Returns
        -------
        None
        """
        if self.client.bucket_exists(bucket_name):
            try:
                self.client.remove_bucket(bucket_name)
                self.log.info(f'deleting the bucket: {bucket_name}')
            except S3Error as e:
                self.log.error(f'could not find the bucket: {bucket_name}: {e}')
        else:
            self.log.error('bucket not found')

    def blob_upload(self, bucket_name: str, blob_name: str, blob_file: str, size: int, meta: dict = {}):
        """Upload a blob to specific bucket.
        Parameters
        ----------
        bucket_name : str
            Specify the name you want to call the bucket. (Be aware about Minios
            naming convetions).
        blob_name : str
            Specify the blob name which is what you will use in other operations regarding the blob.
        blob_file : buffer
            Convert your binary or text file to bytes and wrap it into a buffer for insertion.
        size : int
            Specify the `size` of the byte file such that minio will know how much data is needed
            to be converted into a blob.
        Returns
        -------
        None
        """
        if self.client.bucket_exists(bucket_name):
            try:
                self.client.put_object(
                                bucket_name=bucket_name,
                                object_name=blob_name,
                                data=blob_file,
                                length=size,
                                metadata=meta
                                # sse=self.SSEC
                                )
            except S3Error as e:
                self.log.error(f'failed to upload: {blob_name}: {e}')
        else:
            self.log.error('bucket not found')

    def delete_blobs(self, bucket_name: str, blob_list: list = None, blob_name: str = None):
        """Delete a blob or blobs. The method will either use a single string name
        or a list with string names to delete a blob or several blobs respectivley.
        Parameters
        ----------
        bucket_name : str
            Specify the name you want to call the bucket. (Be aware about Minios
            naming convetions).
        blob_list : list
            A list with string names for the blobs to delete.
        blob_name : str
            A string name of the blob to delete.
        Returns
        -------
        None
        """
        if self.client.bucket_exists(bucket_name):
            try:
                if blob_list:
                    assert blob_name is None, 'only pass a list of blob names when the purpose is to delete many at once'
                    if len(blob_list) > 100:
                        self.log.warning(f'{len(blob_list)} blobs deleted')
                    else:
                        self.log.info(f'{len(blob_list)} blobs deleted')
                    blobs_to_delete = self.client.remove_objects(bucket_name, blob_list)
                    for blob_err in blobs_to_delete:
                        self.log.error(f'could not delete blob: {blob_err}')
                else:
                    assert blob_list is None, 'only pass a blob string name when the purpose is to delete one blob at the time'
                    self.client.remove_object(bucket_name, blob_name)
            except S3Error as e:
                self.log.error(f'failed to set up blob deletion {e}')
        else:
            self.log.error('bucket not found')

    def get_blobs(self, bucket_name: str, blob_list: list = None, blob_name: str = None):
        """Extract a blob or several blobs from the bucket. The method will extract either
        one blob based on a single string name or several blobs with a list of string names.
        You can pass one or the other but not both a list and single string name at the same time.
        Parameters
        ----------
        bucket_name : str
            Specify the name you want to call the bucket. (Be aware about Minios
            naming convetions).
        blob_list : list
            A list of string names for the blobs to extract.
        blob_name : str
            A single string name of the blob to extract.
        Returns
        -------
        HTTPResponse
            The method will return a HTTPResponse containg some HTTP information
            and the data. Use `object_name.data` to extract the data from HTTPResponse.
        """
        if self.client.bucket_exists(bucket_name):
            if blob_list:
                # Check type
                if not isinstance(blob_list, list):
                    self.log.error(f'expected a list of blobs but got type: {type(blob_list)}')
                    raise TypeError

                # clear the dict for when the class method is used in a loop
                config.blob_dict.clear()

                # loop over the list and extract the images into a dict
                for blob in tqdm(
                                blob_list,
                                desc='extracting multiple blobs',
                                total=len(blob_list)
                                ):
                    try:
                        blob_file = self.client.get_object(
                                            bucket_name=bucket_name,
                                            object_name=blob
                                            # sse=self.SSEC
                                            )
                        # NOTE! this is very image specific
                        img = payload_transform(payload=blob_file.data,
                                                shape_str=blob_file.headers.get('x-amz-meta-img_shape'),
                                                dtype_str=blob_file.headers.get('x-amz-meta-dtype')
                                                )
                        config.blob_dict[blob].append(img)
                    except S3Error as e:
                        self.log.error(f'failed to retrieve blob: {e}')
                return config.blob_dict

            else:
                blob_file = self.client.get_object(
                                        bucket_name=bucket_name,
                                        object_name=blob_name
                                        # sse=self.SSEC
                                        )
                img = payload_transform(payload=blob_file.data,
                                        shape_str=blob_file.headers.get('x-amz-meta-img_shape'),
                                        dtype_str=blob_file.headers.get('x-amz-meta-dtype')
                                        )
                return img
        else:
            self.log.error(f'bucket {bucket_name} not found')
