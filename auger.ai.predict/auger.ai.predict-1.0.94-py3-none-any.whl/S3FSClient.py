import boto3
import botocore
import datetime
import json
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
import mimetypes
import os
import time
import uuid

from dateutil.tz import tzutc
from urllib.parse import urlparse

AWS_S3_HOST = "s3.amazonaws.com"

def retry_helper(func, retry_errors=[], num_try=10, delay=10):
    nTry = 0
    while True:
        try:
            return func()
        except Exception as exc:
            retry_exc = False
            if not retry_errors:
                retry_exc = True
            else:
                for retry_error in retry_errors:
                    if retry_error in str(exc):
                        retry_exc = True
                        break

            if retry_exc and nTry < num_try:
                logging.error("Retry '%s', error: '%s'. Sleep and try again. Num try: %s"%(func, str(exc), nTry))

                nTry += 1
                time.sleep(delay*nTry)
            else:
                raise

def retry_handler(decorated):
    def wrapper(self, *args, **kwargs):
        return retry_helper(lambda: decorated(self, *args, **kwargs), ['InvalidAccessKeyId', 'NoSuchKey'])

    return wrapper

class BotoClient:
    def __init__(self, region=None, aws_role_arn=None, endpoint_url=None):
        self.endpoint_url = endpoint_url or os.environ.get('S3_ENDPOINT_URL')
        self.aws_role_arn = aws_role_arn or os.environ.get('AWS_ROLE_ARN')
        self.region = region
        self.client = self._build_client('s3')

    def _build_client(self, service_name):
        return boto3.client(
            service_name,
            endpoint_url=self.endpoint_url,
            config=boto3.session.Config(signature_version='s3v4'),
            region_name=self.region,
        )

    @retry_handler
    def get_waiter(self, *args, **kwargs):
        return self.client.get_waiter(*args, **kwargs)

    @retry_handler
    def list_objects_v2(self, *args, **kwargs):
        return self.client.list_objects_v2(*args, **kwargs)

    @retry_handler
    def put_object(self, *args, **kwargs):
        return self.client.put_object(*args, **kwargs)

    @retry_handler
    def head_bucket(self, *args, **kwargs):
        return self.client.head_bucket(*args, **kwargs)

    @retry_handler
    def create_bucket(self, *args, **kwargs):
        return self.client.create_bucket(*args, **kwargs)

    @retry_handler
    def delete_bucket(self, Bucket):
        self._delete_items(Bucket, "list_objects", "Contents")
        self._delete_items(Bucket, "list_object_versions", "Versions")
        self._delete_items(Bucket, "list_object_versions", "DeleteMarkers")

        self.client.delete_bucket(Bucket=Bucket)

    def _map_version_key(self, obj):
        res = {"Key": obj["Key"]}

        if "VersionId" in obj:
            res["VersionId"] = obj["VersionId"]

        return res

    def _delete_items(self, bucket, method_name, resource_name):
        batch_delete_limit = 1000 # delete_objects can't delete more that 1000 keys at once
        list_func = lambda: getattr(self.client, method_name)(Bucket=bucket, MaxKeys=batch_delete_limit).get(resource_name, [])

        items = list_func()
        while len(items) > 0:
            keys = list(map(self._map_version_key, items))
            self.client.delete_objects(Bucket=bucket, Delete={'Objects': keys})
            items = list_func()

    @retry_handler
    def delete_object(self, *args, **kwargs):
        return self.client.delete_object(*args, **kwargs)

    @retry_handler
    def copy_object(self, *args, **kwargs):
        return self.client.copy_object(*args, **kwargs)

    @retry_handler
    def head_object(self, *args, **kwargs):
        return self.client.head_object(*args, **kwargs)

    @retry_handler
    def list_objects(self, *args, **kwargs):
        return self.client.list_objects(*args, **kwargs)

    @retry_handler
    def download_file(self, *args, **kwargs):
        return self.client.download_file(*args, **kwargs)

    @retry_handler
    def upload_file(self, *args, **kwargs):
        return self.client.upload_file(*args, **kwargs)

    @retry_handler
    def copy(self, *args, **kwargs):
        return self.client.copy(*args, **kwargs)

    @retry_handler
    def generate_presigned_url_ex(self, bucket, key, method="GET", expires_in=None, max_content_length=None):
        response = self.client.get_bucket_location(Bucket=bucket)

        s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            config=boto3.session.Config(
                signature_version='s3v4',
                region_name=response.get('LocationConstraint'),
                s3={'addressing_style': 'virtual'},
            )
        )

        if method == 'POST':
            conditions = [{"success_action_status": "200"}]

            if max_content_length:
                conditions.append(["content-length-range", 0, max_content_length])

            return s3_client.generate_presigned_post(
                Bucket=bucket,
                Key=key,
                ExpiresIn=expires_in or 3600,
                Fields={'success_action_status': 200},
                Conditions=conditions,
            )
        elif method == "GET" or method == "PUT":
            client_method = 'get_object'

            if method == 'PUT':
                client_method = 'put_object'

            return s3_client.generate_presigned_url(
                ClientMethod=client_method,
                ExpiresIn=expires_in,
                Params={
                    'Bucket': bucket,
                    'Key': key
                },
            )
        else:
            raise ValueError(f"unexpected method: '{method}'")

    @retry_handler
    def get_multipart_upload_config(self, bucket, key, expires_in=None):
        sts_client = self._build_client('sts')

        response = sts_client.assume_role(
            RoleArn=self.aws_role_arn,
            RoleSessionName='upload_' + str(uuid.uuid4()),
            DurationSeconds=expires_in,
            Policy=self._build_upload_polciy(bucket, key)
        )

        credentials = response["Credentials"]
        endpoint = self.client._endpoint.host
        parsed_url = urlparse(endpoint)

        # Multipart upload requires host if format: "Host: Bucket.s3.amazonaws.com"
        # see https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateMultipartUpload.html
        # but Minio requires plain URL, so check netloc and insert bucket only for AWS S3
        if parsed_url.netloc == AWS_S3_HOST:
            endpoint = None

        return {
            "bucket": bucket,
            "key": key,
            "config": {
                "endpoint": endpoint,
                "port": parsed_url.port or 443,
                "use_ssl": True,
                "access_key": credentials["AccessKeyId"],
                "secret_key": credentials["SecretAccessKey"],
                "security_token": credentials["SessionToken"],
            }
        }

    def _build_upload_polciy(self, bucket, key):
        return json.dumps(
            {
                "Version": '2012-10-17',
                "Statement": [
                    {
                        "Action": [
                            "s3:*",
                        ],
                        "Effect": "Allow",
                        "Resource": [
                            f"arn:aws:s3:::{bucket}/{key}"
                        ],
                    }
                ]
            }
        )

    def get_waiter_names(self):
        return self.client.waiter_names

class S3FSClient:
    @staticmethod
    def split_path_to_bucket_and_key(path):
        uri = urlparse(path)

        rel_path = uri.path[1:]
        rel_path = rel_path.replace("//", "/")
        if rel_path.endswith("/"):
            rel_path = rel_path[:-1]

        return uri.netloc, rel_path

    def _getRelativePath(self, path):
        self.s3BucketName, rel_path = S3FSClient.split_path_to_bucket_and_key(path)
        self.client = BotoClient()
        return rel_path

    def get_smart_open_transport_params(self):
        transport_params = None
        endpoint_url = os.environ.get('S3_ENDPOINT_URL')

        if endpoint_url:
            transport_params = {
                'resource_kwargs': {
                    'endpoint_url': endpoint_url,
                }
            }

        return transport_params

    def generate_presigned_url(self, path):
        try:
            path = self._getRelativePath(path)

            return self.client.generate_presigned_url_ex(self.s3BucketName, path)
        except Exception as e:
            logging.error("generate_presigned_url failed: %s"%e)

        return None

    def wait_for_path(self, path):
        path = self._getRelativePath(path)
        if 'object_exists' in self.client.get_waiter_names():
            waiter = self.client.get_waiter('object_exists')
            waiter.config.delay = 2
            waiter.config.max_attempts = 50

            logging.info("S3FSClient: waiting for max %s sec for object: %s" % (
                waiter.config.delay*waiter.config.max_attempts, path))
            waiter.wait(Bucket=self.s3BucketName, Key=path)

    def s3fs_open(self, path, mode):
        from s3fs.core import S3FileSystem

        endpoint_url = os.environ.get('S3_ENDPOINT_URL')
        client_kwargs = {}
        if endpoint_url:
            client_kwargs = {'endpoint_url': endpoint_url}

        if 'r' in mode:
            self.wait_for_path(path)

        s3 = S3FileSystem(anon=False, default_fill_cache=False, client_kwargs=client_kwargs)
        return s3.open(path, mode=mode)

    def listFolder(self, path, wild=False, removeFolderName=True, meta_info=False):
        import fnmatch
        from urllib.parse import unquote

        path_arg = path
        path = self._getRelativePath(path)
        path_filter = None
        if path and wild:
            parts = path.split('/')
            path = '/'.join(parts[:-1])
            path_filter = parts[-1]
            parts = path_arg.split('/')
            path_arg = '/'.join(parts[:-1])

        if path:
            path = path + "/" if not path.endswith("/") else path

        #print("s3BucketName: %s;Path:%s; path_filter:%s"%(self.s3BucketName, path, path_filter))

        ContinuationToken = None
        result = []
        while True:
            if ContinuationToken:
                listFiles = self.client.list_objects_v2(
                    Bucket=self.s3BucketName, Prefix=path, Delimiter='/', ContinuationToken=ContinuationToken)
            else:
                listFiles = self.client.list_objects_v2(
                    Bucket=self.s3BucketName, Prefix=path, Delimiter='/')

            ContinuationToken = listFiles.get('NextContinuationToken', None)
            files = None
            folders = None
            if listFiles is not None:
                files = listFiles.get('Contents')
                folders = listFiles.get('CommonPrefixes')

            if files is not None:
                for file in files:
                    if file.get('Key') != path:
                        file_path = unquote(file.get('Key')[len(path):])
                        if meta_info:
                            result.append({'path': file_path,
                                'last_modified': self._get_seconds_from_epoch(file.get('LastModified')), 'size': file.get('Size', 0)})
                        else:
                            result.append(file_path)

            if folders is not None:
                for folder in folders:
                    if folder.get('Prefix') != path:
                        folder_path = unquote(folder.get('Prefix')[len(path):])
                        if meta_info:
                            result.append({'path': folder_path,
                                'last_modified': self._get_seconds_from_epoch(folder.get('LastModified')), 'size': folder.get('Size', 0)})
                        else:
                            result.append(folder_path)

            if not ContinuationToken:
                break

        if path_filter:
            if meta_info:
                result = [item for item in result if fnmatch.fnmatch(item['path'], path_filter)]
            else:
                result = fnmatch.filter(result, path_filter)

        if not removeFolderName:
            for idx, item in enumerate(result):
                if meta_info:
                    result[idx]['path'] = os.path.join(path_arg, item['path'])
                else:
                    result[idx] = os.path.join(path_arg, result[idx])

        return result

    def createFolder(self, path):
        path = self._getRelativePath(path)
        path = path + "/" if not path.endswith("/") else path

        # If no path we shouldn't create it
        if path != "/":
            self.client.put_object(Bucket=self.s3BucketName, Key=path.lstrip('/'))

    def createParentFolder(self, path):
        parent = os.path.dirname(path)
        if parent:
            self.createFolder(parent)

    def ensure_bucket_deleted(self, Bucket):
        try:
            self.client = BotoClient()
            self.client.head_bucket(Bucket=Bucket)
            self.client.delete_bucket(Bucket=Bucket)
        except botocore.client.ClientError as e:
            code = e.response['Error']['Code']
            # 404 - deleted, that how it should work
            # 400 - looks like a bug in S3 API, it's returned for deleted versioned buckets
            # same as in https://github.com/aws/aws-sdk-js/issues/2749
            if code == '404' or code == '400':
                return True
            else:
                raise


    def removeFolder(self, path, remove_self=True):
        path = self._getRelativePath(path)
        self._s3_removeFolder(path, remove_self)

    def removeFile(self, path, wild=False):
        try:
            if wild:
                files = self.listFolder(path, wild)
                path = self._getRelativePath(path)
                for file in files:
                    path_to_remove = os.path.join(os.path.dirname(path), file)
                    # print(path_to_remove)
                    self.client.delete_object(
                        Bucket=self.s3BucketName, Key=path_to_remove)

                #raise Exception("S3FSClient::remove_file wild is not implemented:%s"%path)
            else:
                path = self._getRelativePath(path)
                self.client.delete_object(Bucket=self.s3BucketName, Key=path)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchBucket':
                raise

    def _s3_removeFolder(self, path, remove_self=True):
        path = path + "/" if not path.endswith("/") else path

        # print("Remove:%s"%path)
        ContinuationToken = None
        while True:
            if ContinuationToken:
                listFiles = self.client.list_objects_v2(
                    Bucket=self.s3BucketName, Prefix=path, Delimiter='/', ContinuationToken=ContinuationToken)
            else:
                listFiles = self.client.list_objects_v2(
                    Bucket=self.s3BucketName, Prefix=path, Delimiter='/')

            # print(listFiles)
            ContinuationToken = listFiles.get('NextContinuationToken', None)
            files = None
            folders = None
            if listFiles is not None:
                files = listFiles.get('Contents')
                folders = listFiles.get('CommonPrefixes')

            if files is not None:
                for file in files:
                    #print("Delete path:%s"%file.get('Key'))
                    self.client.delete_object(
                        Bucket=self.s3BucketName, Key=file.get('Key'))

            if folders is not None:
                for folder in folders:
                    self._s3_removeFolder(folder.get(
                        'Prefix'), remove_self=False)

            if not ContinuationToken:
                break

        if remove_self:
            self.client.delete_object(Bucket=self.s3BucketName, Key=path[:-1])

    def _s3_moveFile(self, oldName, newName):
        self.client.copy_object(Bucket=self.s3BucketName, CopySource={
                                'Bucket': self.s3BucketName, 'Key': oldName}, Key=newName)
        self.client.delete_object(Bucket=self.s3BucketName, Key=oldName)

    def isFileExists(self, path):
        path = self._getRelativePath(path)
        exists = False
        try:
            res = self.client.head_object(Bucket=self.s3BucketName, Key=path)
            exists = True
        except Exception as e:
            pass

        return exists

    @staticmethod
    def _get_seconds_from_epoch(date_data):
        res = 0
        try:
            if date_data:
                epoch = datetime.datetime(1970, 1, 1, tzinfo=tzutc())
                res = (date_data - epoch).total_seconds()
        except Exception as e:
            #logging.exception("_get_seconds_from_epoch failed.")
            pass

        return res

    def getMTime(self, path):
        path = self._getRelativePath(path)
        res = None
        try:
            obj = self.client.head_object(Bucket=self.s3BucketName, Key=path)
            res = self._get_seconds_from_epoch(obj.get('LastModified'))
        except Exception as e:
            #logging.exception("getMTime failed.")
            pass

        return res

    def getFileSize(self, path):
        path = self._getRelativePath(path)
        res = 0
        try:
            obj = self.client.head_object(Bucket=self.s3BucketName, Key=path)
            res = obj.get('ContentLength')
        except Exception as e:
            #logging.exception("getFileSize failed.")
            pass

        return res

    def isDirExists(self, path):
        path = self._getRelativePath(path)
        listFiles = self.client.list_objects(
            Bucket=self.s3BucketName, Prefix=path + "/", Delimiter='/')
        if listFiles is not None:
            content = listFiles.get('Contents')
            if content is None:
                listFiles = listFiles.get('CommonPrefixes')
            else:
                listFiles = content

        #print(listFiles)
        return listFiles is not None

    def readTextFile(self, path):
        from .LocalFSClient import LocalFSClient

        with LocalFSClient().save_atomic(path) as local_tmp_path:
            self.downloadFile(path, local_tmp_path)
            return LocalFSClient().readTextFile(local_tmp_path)

        # obj = self.client.get_object(Bucket=self.s3BucketName, Key=path)
        # return obj['Body'].read()

    def writeTextFile(self, path, data, atomic=False, mode="w"):
        #TODO: support mode="a"
        path = self._getRelativePath(path)
        mimetype, encoding = mimetypes.guess_type(path)
        args = {}
        if mimetype:
            args['ContentType'] = mimetype
        if encoding:
            args['ContentType'] = "application/octet-stream"

        self.client.put_object(Body=data, Bucket=self.s3BucketName, Key=path, **args)

    def copyFileRemote(self, path_src, path_dst):
        path = self._getRelativePath(path_src)
        copy_source = {
            'Bucket': self.s3BucketName,
            'Key': path
        }

        path = self._getRelativePath(path_dst)
        self.client.copy(copy_source, self.s3BucketName, path)

    def copyFile(self, path_src, path_dst):
        if path_src.startswith("s3") and path_dst.startswith("s3"):
            self.copyFileRemote(path_src, path_dst)
        elif path_dst.startswith("s3"):
            path = self._getRelativePath(path_dst)
            self._s3_upload_file(path_src, path)
        elif path_src.startswith("s3"):
            self.downloadFile(path_src, path_dst)

    def _s3_upload_file(self, path_local, path_s3):
        s3_config = boto3.s3.transfer.TransferConfig(use_threads=False)
        mimetype, encoding = mimetypes.guess_type(path_local)
        args = {}
        if mimetype:
            args['ContentType'] = mimetype
        if encoding:
            args['ContentType'] = "application/octet-stream"

        self.client.upload_file(path_local, Bucket=self.s3BucketName, Key=path_s3, Config=s3_config,
            ExtraArgs=args
        )

    def copyFiles(self, path_src, path_dst):
        files = self.listFolder(path_src, wild=True)
        for file in files:
            self.copyFile(os.path.join(os.path.dirname(path_src), file), os.path.join(path_dst, file))

    def copyFolder(self, path_src, path_dst):
        from .FSClient import FSClient

        files = FSClient().listFolder(path_src)
        for file in files:
            full_src = os.path.join(path_src, file)
            if FSClient().isFileExists(full_src):
                self.copyFile(full_src, os.path.join(path_dst, file))
            else:
                self.copyFolder(full_src, os.path.join(path_dst, file))

    def downloadFile(self, path, local_path):
        from .LocalFSClient import LocalFSClient

        try:
            from urllib.parse import urlparse
        except ImportError:
            from urlparse import urlparse

        if path.startswith("http:") or path.startswith("https:"):
            s3_path = self._getRelativePath(local_path)

            uri = urlparse(path)

            with LocalFSClient().save_atomic(uri.path) as temp_file:
                LocalFSClient().downloadFile(path, temp_file)
                self._s3_upload_file(temp_file, s3_path)
        else:
            path = self._getRelativePath(path)
            LocalFSClient().createParentFolder(local_path)
            self.client.download_file(Bucket=self.s3BucketName, Key=path, Filename=local_path)

    def downloadFolder(self, path, local_path):
        files = self.listFolder(path)
        for file in files:
            if file.endswith('/'):
                self.downloadFolder(os.path.join(path, file), os.path.join(local_path, file))
            else:
                self.copyFile(os.path.join(path, file), os.path.join(local_path, file))

    def moveFile(self, path_src, path_dst):
        self.copyFile(path_src, path_dst)

        if path_src.startswith("s3"):
            self.removeFile(path_src)
        else:
            from .LocalFSClient import LocalFSClient
            LocalFSClient().removeFile(path_src)
