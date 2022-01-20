import os
import shutil
import tempfile
import unittest
from unittest import mock
from unittest.mock import call, Mock, patch

from ch.zbindenonline.weatherstation.config import PicturesConfig
from ch.zbindenonline.weatherstation.publishPictures import Main
from ch.zbindenonline.weatherstation.publishPictures import get_pictures
from ch.zbindenonline.weatherstation.restServicePictures import Response, RestServicePictures


def create_pictures_config(picture_dir='picture_dir', delete_after_publish: bool = True) -> PicturesConfig:
    return PicturesConfig('client_id',
                          'client_secret',
                          'username',
                          'password',
                          picture_dir,
                          'picture_url',
                          'camera_id',
                          delete_after_publish)


def create_main(service: RestServicePictures, picture_dir: str = 'picture_dir',
                delete_after_publish: bool = True):
    return MainMock(service, create_pictures_config(picture_dir, delete_after_publish))


class PublishPicturesTest(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_pictures(self):
        jpg = self.createPicture('2021-04-11_114400.jpg')
        webp = self.createPicture('2021-04-11_115100.webp')
        self.createPicture('2021-04-11_115200.txt')

        result = get_pictures(self.test_dir)

        self.assertEqual(2, len(result))
        self.assertIn(jpg, result)
        self.assertIn(webp, result)

    def test_Main_withNoPictures(self):
        service = Mock()
        pictures = []
        main = create_main(service)

        main.run(pictures)

        self.assertFalse(service.called)

    @mock.patch('os.remove')
    def test_Main_withPicturesWithDeleting(self, os_remove):
        service = Mock()
        pictures = ['testPicture1.jpg', 'testPicture2.jpg']
        main = create_main(service, delete_after_publish=True)
        service.post_picture.return_value = Response.OK

        main.run(pictures)

        service.login.assert_called_once()
        service_calls = service.post_picture.call_args_list
        self.assertEqual(call('testPicture1.jpg'), service_calls[0])
        self.assertEqual(call('testPicture2.jpg'), service_calls[1])
        remove_calls = os_remove.call_args_list
        self.assertEqual(call('testPicture1.jpg'), remove_calls[0])
        self.assertEqual(call('testPicture2.jpg'), remove_calls[1])
        service.logout.assert_called_once()

    @mock.patch('os.remove')
    def test_Main_withPicturesWithNoDeleting(self, os_remove):
        service = Mock()
        pictures = ['testPicture1.jpg', 'testPicture2.jpg']
        main = create_main(service, delete_after_publish=False)
        service.post_picture.return_value = Response.OK

        main.run(pictures)

        service.login.assert_called_once()
        service_calls = service.post_picture.call_args_list
        self.assertEqual(call('testPicture1.jpg'), service_calls[0])
        self.assertEqual(call('testPicture2.jpg'), service_calls[1])
        remove_calls = os_remove.call_args_list
        self.assertEqual(0, len(remove_calls))
        service.logout.assert_called_once()

    @patch('shutil.move')
    def test_Main_whenPictureExistsAlready(self, shutil_move):
        service = Mock()
        pictures = ['testPicture.jpg']
        main = create_main(service, 'testDirWhenPicturesExistAlready')
        service.post_picture.return_value = Response.DUPLICATE

        main.run(pictures)

        service.login.assert_called_once()
        service.post_picture.assert_called_with('testPicture.jpg')
        shutil_move.assert_called_with('testPicture.jpg', 'testDirWhenPicturesExistAlready/existing',
                                       copy_function=shutil.copytree)
        service.logout.assert_called_once()

    @patch('shutil.move')
    def test_Main_whenUnprocessableEntity(self, shutil_move):
        service = Mock()
        pictures = ['testPicture.jpg']
        main = create_main(service, 'unprocessableTestDir')
        service.post_picture.return_value = Response.UNPROCESSABLE_ENTITY

        main.run(pictures)

        service.login.assert_called_once()
        service.post_picture.assert_called_with('testPicture.jpg')
        shutil_move.assert_called_with('testPicture.jpg', 'unprocessableTestDir/existing',
                                       copy_function=shutil.copytree)
        service.logout.assert_called_once()

    def createPicture(self, name):
        picture = os.path.join(self.test_dir, name)
        f = open(picture, 'w')
        f.write('This is a kind of picture')
        f.close()
        return picture


class MainMock(Main):
    def __init__(self, service: RestServicePictures, config: PicturesConfig):
        super().__init__(config)
        self.service = service

    def __create_service(self, config: PicturesConfig) -> RestServicePictures:
        return self.service


if __name__ == '__main__':
    unittest.main()
