import sys
from botocore.config import Config
from botocore.errorfactory import ClientError

from awsservicespkg.utils import constants


class S3Service:
    # Instantiate S3 service
    def __init__(self, _logger, session, aws_region):
        try:
            self.s3_client = session.client('s3', region_name=aws_region, config=Config(retries=dict(max_attempts=3)))
            self.logger = _logger
            self.logger.info('S3 client initialized')
        except Exception as e:
            _logger.exception(e)
            print("Error while creating S3 client. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def read_s3_file(self, bucket, bucket_key):
        try:
            obj = self.s3_client.get_object(Bucket=bucket, Key=bucket_key)
            contents = obj['Body'].read().decode('utf-8')
            return contents
        except Exception as err:
            self.logger.exception(err)
            print("Error while reading {} from s3. Please refer to the log file at- ".format(bucket_key)
                  + constants.logger_path)
            sys.exit(1)

    def upload_files_to_s3(self, local_files_directory_path, list_of_file_names, _bucket_name, upload_path_on_s3):
        try:
            for filename in list_of_file_names:
                self.s3_client.upload_file(local_files_directory_path + "/" + filename, _bucket_name,
                                           upload_path_on_s3 + '/' + filename)
                self.logger.info(
                    local_files_directory_path + "\\" + filename + " uploaded to s3 bucket- " + _bucket_name)
        except Exception as e:
            self.logger.exception(e)
            print("Error while uploading files to s3. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def download_file_from_bucket(self, bucket_name, local_path_to_download, bucket_key):
        try:
            self.s3_client.download_file(Bucket=bucket_name, Filename=local_path_to_download, Key=bucket_key)
            self.logger.info(bucket_name + '/' + bucket_key + ' file downloaded as ' + local_path_to_download)
        except Exception as e:
            self.logger.exception(e)
            print("Error while downloading file from s3. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def list_bucket_files(self, bucket, bucket_key, file_extension):
        try:
            bucket_contents = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=bucket_key)
            file_list = []
            if file_extension:
                for file_object in bucket_contents['Contents']:
                    if file_object['Key'].endswith('.' + file_extension):
                        file_name = file_object['Key'].replace(bucket_key + '/', '')
                        if file_name:
                            file_list.append(file_name)
            else:
                for file_object in bucket_contents['Contents']:
                    file_name = file_object['Key'].replace(bucket_key + '/', '')
                    if file_name:
                        file_list.append(file_name)
            return file_list
        except Exception as e:
            self.logger.exception(e)
            print("Error while listing files from s3. Please refer to the log file at- " + constants.logger_path)
            sys.exit(1)

    def copy_file_from_src_to_dest_bucket(self, src_bucket_name, src_bucket_key, dest_bucket_name, dest_bucket_key):
        source_file = src_bucket_name + '/' + src_bucket_key
        dest_file = dest_bucket_name + '/' + dest_bucket_key
        try:
            copy_source = {
                'Bucket': src_bucket_name,
                'Key': src_bucket_key
            }
            self.s3_client.copy(copy_source, dest_bucket_name, dest_bucket_key)
        except Exception as e:
            self.logger.exception(e)
            print("Error while copying {} to {}. Please refer to the log file at- ".format(source_file, dest_file)
                  + constants.logger_path)
            sys.exit(1)

    def delete_file_from_s3(self, bucket_name, bucket_key):
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=bucket_key)
            self.logger.info('{} deleted successfully.'.format(bucket_name + '/' + bucket_key))
        except Exception as e:
            self.logger.exception(e)
            print("Error while deleting file- {}. Please refer to the log file at- ".format(
                bucket_name + '/' + bucket_key)
                  + constants.logger_path)
            sys.exit(1)

    def create_file_in_s3(self, bucket_name, bucket_key, file_data):
        file_name = bucket_key.split('/')[-1]
        try:
            self.s3_client.put_object(Body=file_data, Bucket=bucket_name, Key=bucket_key)
            self.logger.info('{} created/updated successfully in s3 bucket.'.format(file_name))
        except Exception as e:
            self.logger.exception(e)
            print("Error while creating/updating file- {} in s3 bucket- {}".format(file_name, bucket_name))
            sys.exit(1)

    def check_if_key_exists(self, bucket_name, bucket_key):
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=bucket_key)
            self.logger.info('key- {} exists in bucket- {}'.format(bucket_key, bucket_name))
            return True
        except ClientError:
            self.logger.warning('key- {} does not exist in bucket- {}'.format(bucket_key, bucket_name))
            return False
