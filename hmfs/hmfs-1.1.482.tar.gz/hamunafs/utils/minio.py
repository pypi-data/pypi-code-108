import traceback
from minio import Minio


class MinioAgent:
    def __init__(self, endpoint, acs_key, secret_key, secure=True, location='default'):
        self.client = Minio(endpoint, access_key=acs_key, secret_key=secret_key, secure=secure, region=location)
        self.location = location

    def create_bucket_if_not_exists(self, bucket_name, location):
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name, location=location)
            
            return True
        except Exception as e:
            traceback.print_exc()
            return False
    
    def upload_file(self, path, bucket, bucket_filename, tries=0):
        try:
            if self.create_bucket_if_not_exists(bucket, self.location):
                self.client.fput_object(bucket, bucket_filename, path)
                return True, 'minio://{}/{}'.format(bucket, bucket_filename)
            else:
                print('創建bucket失敗: {}'.format(bucket))
                return False, '創建bucket失敗'
        except Exception as e:
            if tries > 3:
                return False, e
            else:
                return self.upload_file(path, bucket, bucket_filename, tries+1)

    def upload_file_by_buffer(self, buffer, bucket, bucket_filename, tries=0):
        try:
            if self.create_bucket_if_not_exists(bucket, self.location):
                self.client.put_object(bucket, bucket_filename, buffer, len(buffer.getvalue()))
                return True, 'minio://{}/{}'.format(bucket, bucket_filename)
            else:
                return False, '創建bucket失敗'
        except Exception as e:
            if tries > 3:
                return False, e
            else:
                return self.upload_file_by_buffer(buffer, bucket, bucket_filename, tries+1)

    def download_file(self, path, bucket, bucket_filename, tries=0):
        try:
            self.client.fget_object(bucket, bucket_filename, path)
            return True, path
        except Exception as e:
            if tries > 5:
                return False, e
            else:
                return self.download_file(path, bucket, bucket_filename, tries+1)
            
    def delete(self, bucket, bucket_name, tries):
        try:
            self.client.remove_object(bucket, bucket_name)
            return True, None
        except Exception as e:
            if tries > 5:
                return False, e
            else:
                return self.delete(bucket, bucket_name, tries + 1)

    def exists(self, bucket, bucket_name):
        meta = self.client.stat_object(bucket, bucket_name)

        return meta is not None



