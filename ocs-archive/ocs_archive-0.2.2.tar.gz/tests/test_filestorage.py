import os
import shutil
from unittest.mock import patch
import unittest

from ocs_archive.storage.filestore import FileStore, FileStoreSpecificationError
from ocs_archive.storage.filesystemstore import FileSystemStore
from ocs_archive.storage.filestorefactory import FileStoreFactory
from ocs_archive.storage.s3store import strip_quotes_from_etag, S3Store
from ocs_archive.input.file import File
from ocs_archive.input.lcofitsfile import LcoFitsFile


FITS_PATH = os.path.join(
    os.path.dirname(__file__),
    'test_files/fits/'
)
OTHER_PATH = os.path.join(
    os.path.dirname(__file__),
    'test_files/other/'
)
FITS_FILE = os.path.join(
    FITS_PATH,
    'coj1m011-kb05-20150219-0125-e90.fits.fz'
)
PDF_FILE = os.path.join(
    OTHER_PATH,
    'cptnrs03-fa13-20150219-0001-e92-summary.pdf'
)


def mocked_s3_object(*args, **kwargs):
    class MockS3Object:
        class Object:
            def __init__(self, *args, **kwargs):
                pass

            def put(self, *args, **kwargs):
                return {'ETag': '"fakemd5"', 'VersionId': 'fakeversion'}

    return MockS3Object()

def mocked_boto3_client(*args, **kwargs):
    class MockBoto3Client:
        def __init__(self, *args, **kwargs):
            pass

        def download_fileobj(self, Bucket, Key, Fileobj):
            filename = os.path.basename(Key)
            Fileobj.write(b"Test 123")
            setattr(Fileobj, 'name', filename)

        def head_object(self, Bucket, Key):
            return {'ContentLength': 10}

        def generate_presigned_url(self, *args, **kwargs):
            params = kwargs['Params']
            return f"s3://{params['Bucket']}/{params['Key']}"

        def delete_object(self, *args, **kwargs):
            pass

    return MockBoto3Client()

class TestS3Store(unittest.TestCase):
    def setUp(self):
        self.s3 = S3Store(bucket='somebucket')

    def test_strip_quotes_from_etag(self):
        self.assertEqual('fakemd5', strip_quotes_from_etag('"fakemd5"'))
        self.assertIsNone(strip_quotes_from_etag('"wrong'))

    @patch('boto3.resource', side_effect=mocked_s3_object)
    def test_upload_file(self, s3_mock):
        with open(FITS_FILE, 'rb') as fileobj:
            data_file = LcoFitsFile(File(fileobj))
            self.s3.store_file(data_file)
        self.assertTrue(s3_mock.called)

    @patch('boto3.client', side_effect=mocked_boto3_client)
    def test_get_file(self, boto3_mock):
        with self.s3.get_fileobj('special/dir/thing.fits.fz') as fileobj:
            self.assertTrue(boto3_mock.called)
            self.assertEqual(fileobj.name, 'thing.fits.fz')

    @patch('boto3.client', side_effect=mocked_boto3_client)
    def test_get_file_size(self, boto3_mock):
        filesize = self.s3.get_file_size('thing.fits.fz')
        self.assertTrue(boto3_mock.called)
        self.assertEqual(filesize, 10)

    @patch('boto3.client', side_effect=mocked_boto3_client)
    def test_get_url(self, boto3_mock):
        url = self.s3.get_url('thing.fits.fz', '', 0)
        self.assertTrue(boto3_mock.called)
        self.assertEqual(url, 's3://somebucket/thing.fits.fz')

    @patch('boto3.client', side_effect=mocked_boto3_client)
    def test_delete_file(self, boto3_mock):
        self.s3.delete_file('thing.fits.fz', '')
        self.assertTrue(boto3_mock.called)


class TestFileSystemStore(unittest.TestCase):
    def setUp(self):
        self.file_system_store = FileSystemStore('./tests/test_output/')
        self.fileobj = open(FITS_FILE, 'rb')
        self.base_file = File(self.fileobj, 'coj1m011-kb05-20150219-0125-e90.fits.fz')
        self.base_fits_file = LcoFitsFile(self.base_file, required_headers=('DATE-OBS', 'PROPID'))

    def tearDown(self):
        self.fileobj.close()

    @unittest.mock.patch('ocs_archive.settings.settings.FILESYSTEM_STORAGE_BASE_URL', 'http://123.0.0.456/')
    def test_get_url(self):
        path = self.base_fits_file.get_filestore_path()
        url = self.file_system_store.get_url(path, '', 0)
        self.assertEqual(url, os.path.join('http://123.0.0.456/', path))

    def test_all_filesystem_operations(self):
        path = self.base_fits_file.get_filestore_path()
        # Save the file to disk
        metadata = self.file_system_store.store_file(self.base_fits_file)
        self.assertEqual(metadata['key'], self.base_file.get_md5())
        self.assertEqual(metadata['md5'], self.base_file.get_md5())
        self.assertEqual(metadata['extension'], self.base_file.extension)

        # Try to get the saved file and compare it to the open one
        with self.file_system_store.get_fileobj(path) as fileobj:
            new_file = File(fileobj, self.base_file.filename)
            data_file = LcoFitsFile(new_file, required_headers=('DATE-OBS', 'PROPID'))
            frame_data = data_file.get_header_data().get_archive_frame_data()
            self.assertDictEqual(frame_data, self.base_fits_file.get_header_data().get_archive_frame_data())

        # check the file size against the created file on disk
        self.assertEqual(self.file_system_store.get_file_size(path), len(self.base_file))

        # Now delete the file so it is cleaned up after running the test
        self.file_system_store.delete_file(path, '')

        # Now try to get the file again and make sure it returns None
        with self.file_system_store.get_fileobj(path) as fileobj:
            self.assertIsNone(fileobj)
        
        # Now remove the whole filesystemstore root_dir to clean up
        shutil.rmtree(self.file_system_store.root_dir)


class TestFileStoreFactory(unittest.TestCase):
    def test_filestore_factory_returns_existing_class(self):
        filestore_class = FileStoreFactory.get_file_store_class('dummy')
        self.assertIs(filestore_class, FileStore)

        filestore_class = FileStoreFactory.get_file_store_class('local')
        self.assertIs(filestore_class, FileSystemStore)

        filestore_class = FileStoreFactory.get_file_store_class('s3')
        self.assertIs(filestore_class, S3Store)

    def test_filestore_factory_raises_exception_for_nonexistent_type(self):
        with self.assertRaises(FileStoreSpecificationError) as fsse:
            FileStoreFactory.get_file_store_class('crazystore')
        self.assertEqual('Invalid FileStore type crazystore', str(fsse.exception))
