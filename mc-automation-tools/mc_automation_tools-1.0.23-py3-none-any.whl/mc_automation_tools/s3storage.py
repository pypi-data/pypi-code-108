# pylint: disable=line-too-long,invalid-name
"""This module provide usefull class that wrapping S3 and provide basic functionality [read and write] with S3 objects"""
import os
import logging
import boto3
import botocore
import requests
from mc_automation_tools.configuration import config

_log = logging.getLogger('automation_tools.s3storage')


class S3Client:
    """
    This class implements s3 functionality
    """
    # pylint: disable=fixme
    def __init__(self, endpoint_url, aws_access_key_id, aws_secret_access_key):
        if 'minio' in endpoint_url:  # todo - refactor as validation check
            endpoint_url = endpoint_url.split('minio')[0]
        self._endpoint_url = endpoint_url
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._download_urls = {}

        try:
            self._resource = boto3.resource('s3', endpoint_url=self._endpoint_url,
                                            aws_access_key_id=self._aws_access_key_id,
                                            aws_secret_access_key=self._aws_secret_access_key)
        except Exception as e:
            _log.error('Failed on sign into s3 with error %s', str(e))
            raise e

        try:
            self._client = boto3.client('s3', endpoint_url=self._endpoint_url,
                                        aws_access_key_id=self._aws_access_key_id,
                                        aws_secret_access_key=self._aws_secret_access_key)

        except Exception as e:
            _log.error('Failed on sign into s3 with error %s', str(e))
            raise e

        _log.info('New s3 client object was created with end point: %s', self._endpoint_url)

    def get_client(self):
        """return initialized s3 client object"""
        return self._client

    def get_resource(self):
        """return initialized s3 resource object"""
        return self._resource


    def create_new_bucket(self, bucket_name):
        """
        This method add new bucket according to provided name
        """
        if not self._resource.Bucket(bucket_name) in self._resource.buckets.all():
            self._resource.create_bucket(Bucket=bucket_name)
            _log.info('New bucket created with name: %s', bucket_name)

        else:
            _log.error('Bucket with name: [%s] already exist on s3, failed on creation', bucket_name)
            raise FileExistsError('Bucket with name: [%s] already exist on s3, failed on creation' % bucket_name)

    def delete_bucket(self, bucket_name):
        """
        This method empty given bucket and delete bucket
        """
        if not self._resource.Bucket(bucket_name) in self._resource.buckets.all():
            raise FileNotFoundError('Bucket with name: [%s] not exist on s3, failed on deletion' % bucket_name)

        self._resource.Bucket(bucket_name).objects.all().delete()
        self._resource.Bucket(bucket_name).delete()

    def empty_bucket(self, bucket_name):
        """
        This method empty the given bucket without deletion of bucket
        """
        if not self._resource.Bucket(bucket_name) in self._resource.buckets.all():
            raise FileNotFoundError('Bucket with name: [%s] not exist on s3, failed on deletion' % bucket_name)

        self._resource.Bucket(bucket_name).objects.all().delete()

    def upload_to_s3(self, full_path, bucket, object_key):
        """
        basic file uploading to s3
        :param full_path: file system location of file to upload
        :param bucket: bucket name to destination uploading
        :param object_key: name of file to uploading into s3
        """
        if not os.path.exists(full_path):
            raise FileExistsError('File not exist on given directory: %s' % full_path)

        try:
            # self._client.upload_file(full_path, bucket, object_key)
            self._resource.Bucket(bucket).upload_file(full_path, object_key)
            _log.info('Success on uploading %s into s3', os.path.basename(full_path))
        except Exception as e:
            _log.error('Failed uploading file [%s] into s3 with error: %s', object_key, str(e))
            raise Exception('Failed uploading file [%s] into s3 with error: %s' % (full_path, str(e)))  # pylint: disable=raise-missing-from

    def download_from_s3(self, bucket, object_key, destination):
        """
        This method download object into local file system. as default on "/tmp/"
        """
        self._resource.Bucket(bucket).download_file(object_key, destination)
        _log.debug('File was saved on: %s', str(destination))

    def create_download_url(self, bucket, object_key):
        """
        Generate new download url from S3 according to specific bucket and object_key.
        Add new key (object_key) into download_urls dictionary
        """
        self._download_urls[":".join([bucket, object_key])] = self._client.generate_presigned_url('get_object',
                                                                                                  Params={'Bucket': bucket,
                                                                                                          'Key': object_key},
                                                                                                  ExpiresIn=config.S3_DOWNLOAD_EXPIRATION_TIME)
    def is_bucket_exists(self,bucket_name):
        """
        This method check specific bucket on s3 connection if exists
        :param bucket_name: name of specific bucket
        :return: tuple included - bool-exists or not, int-status code of response from bucket, str-string with message response
        """
        try:
            res = self.get_resource().meta.client.head_bucket(Bucket=bucket_name)
            _log.info(f"Bucket: [{bucket_name}] Exists!")
            return True, res['ResponseMetadata']['HTTPStatusCode'], 'Exists'
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 403:
                _log.error(f" {bucket_name} is private Bucket. Forbidden Access!")
                return True, error_code, 'Forbidden Access'
            elif error_code == 404:
                _log.error(f"{bucket_name} bucket Does Not Exist!")
                return False, error_code, 'bucket Does Not Exist'

    def _is_object_exists(self, bucket_name, path):
        bucket = self._resource.Bucket(bucket_name)
        for object_summary in bucket.objects.filter(Prefix=path):
            return True
        return False


    def delete_folder(self,bucket_name, object_key):
        """
        Will delete entire folder on provided bucket
        """
        if not self._is_object_exists(bucket_name, object_key):
            return True
        try:
            objects_to_delete = self._resource.meta.client.list_objects(Bucket=bucket_name, Prefix=object_key)
            delete_keys = {'Objects': []}
            delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]

            self._resource.meta.client.delete_objects(Bucket=bucket_name, Delete=delete_keys)

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False

            _log.error(str(e))
            raise e
        except Exception as e2:
            _log.error(str(e2))
            raise e2

    def is_file_exist(self, bucket_name, object_key):
        """
        Validate if some file exists on specific bucket in OS based on provided object key and bucket name
        """
        if not self._resource.Bucket(bucket_name) in self._resource.buckets.all():
            _log.debug('Bucket with name: [%s] not exist on s3', bucket_name)
            return False

        try:
            self._resource.Object(bucket_name, object_key).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False

            _log.error(str(e))
            raise e
        except Exception as e2:
            _log.error(str(e2))
            raise e2

        return True
        # def get_download_urls(self):
        # return self._download_urls

    def list_folder_content(self, bucket_name, directory_name):
        """

        :return:
        """
        bucket = self._resource.Bucket(bucket_name)
        #
        #
        # for object_summary in bucket.objects.filter(Prefix=f"{directory_name}/"):
        #     print(object_summary.key)
        results = [name.key for name in bucket.objects.filter(Prefix=f"{directory_name}/")]
        return results

def check_s3_valid(end_point, access_key, secret_key, bucket_name=None):
    """
    This method validate correct connection to s3
    :param end_point: base end point url to s3 server
    :param access_key: aws access key
    :param secret_key: aws secret key
    :param bucket_name: specific s3 known exists bucket

    :return: dict with the follow info url_valid & status_code & content & error_msg
    """
    resp_dict = {'url_valid': False, 'status_code': None, 'content': None, 'error_msg': None}

    try:
        resp = requests.get(end_point)
        if resp.status_code > 200 or resp.status_code < 500:
            resp_dict['url_valid'] = True
            resp_dict['status_code'] = resp.status_code
            resp_dict['content'] = resp.content

            s3_conn = S3Client(end_point, access_key, secret_key)
            res = s3_conn.is_bucket_exists(bucket_name)
            resp_dict['url_valid'] = res[0]
            resp_dict['status_code'] = res[1]
            resp_dict['content'] = res[2]
        else:
            resp_dict['url_valid'] = False
            resp_dict['status_code'] = resp.status_code
            resp_dict['content'] = resp.content
            resp_dict['error_msg'] = 'error on url'


    except Exception as e:
        _log.error(f'unable connect to current url: [{end_point}]\nwith error of [{str(e)}]')
        resp_dict['error_msg'] = str(e)


    return resp_dict


    # s3_conn = s3storage.S3Client(end_point, access_key, secret_key)