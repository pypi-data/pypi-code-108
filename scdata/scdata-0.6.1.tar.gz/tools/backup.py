try:
    from boto3 import resource
except ModuleNotFoundError:
    pass

import time
import os
from os.path import join, abspath, dirname
from traceback import print_exc

class S3handler:
    """
    Class that uploads or downloads files to s3 bucket
    """

    def __init__(self, public = False, verbose = True):

        error = False
        try:
            S3_DATA_BUCKET = os.environ['S3_DATA_BUCKET']
            S3_PUBLIC_BUCKET = os.environ['S3_PUBLIC_BUCKET']
        except KeyError:
            error = True
            pass
        else:
            print ('Loaded environment keys')
        finally:
            if error:
                print ("ERROR WHILE LOADING S3HANDLER - REVIEW KEYS")
                return

        if public:
            self.S3_BUCKET = S3_PUBLIC_BUCKET
        else:
            self.S3_BUCKET = S3_DATA_BUCKET

        self.bucket = resource('s3').Bucket(self.S3_BUCKET)
        self.verbose = verbose
        self.public = public

    def std_out(self, msg, type_message = None, force = False):
        if self.verbose or force:
            if type_message is None: print(msg)
            elif type_message == 'SUCCESS': print(f'[SUCCESS] {msg}')
            elif type_message == 'WARNING': print(f'[WARNING] {msg}')
            elif type_message == 'ERROR': print(f'[ERROR] {msg}')

    def get_objects(self):

        objects = self.bucket.all()

        object_names = [obj.name for obj in objects]
        if object_names is not None:
            self.std_out(f'Successfully got keys in bucket {self.bucket.name}', 'SUCCESS')
            return object_names
        else:
            self.std_out(f'No keys in bucket {self.bucket}', 'ERROR')
            return None

    def download(self, filename, s3filename = ''):

        if s3filename == '': s3filename = os.path.basename(filename)
        self.std_out(f'Target file name for download: {s3filename}')

        self.bucket.download_file(s3filename, filename)
        self.std_out(f'Downloaded files to {filename}')

    def upload(self, filename, s3filename = '', url = True):
        '''
            Only for public website repos now
        '''

        if s3filename == '': s3filename = os.path.basename(filename)
        self.std_out(f'Target file name for upload: {s3filename}')

        self.bucket.upload_file(filename, s3filename)
        if url == True and self.public:
            response = f'https://{self.bucket.name}/{s3filename}'
            self.std_out(f'URL {response}')
            return response

        # The response contains the presigned URL
        self.std_out(f'Uploaded files from {filename} to {s3filename}', 'SUCCESS')

        return True
