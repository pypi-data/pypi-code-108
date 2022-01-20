import os
import shutil
import tempfile
import unittest
from unittest.mock import call, Mock, patch

from ch.zbindenonline.weatherstation.publishPictures import Main
from ch.zbindenonline.weatherstation.publishPictures import get_pictures
from ch.zbindenonline.weatherstation.restServicePictures import Response


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
        main = Main(service, pictures, False)
        main.run()
        self.assertFalse(service.called)

    def test_Main_withPictures(self):
        service = Mock()
        pictures = ['testPicture1.jpg', 'testPicture2.jpg']
        main = Main(service, pictures, False)
        main.run()
        service.login.assert_called_once()
        calls = service.post_picture.call_args_list
        self.assertEqual(call('testPicture1.jpg'), calls[0])
        self.assertEqual(call('testPicture2.jpg'), calls[1])
        service.logout.assert_called_once()

    @patch('shutil.move')
    def test_Main_whenPictureExistsAlready(self, shutil_move):

        response = Response.DUPLICATE
        service = Mock()
        pictures = ['testPicture.jpg']
        main = Main(service, pictures, False)
        service.post_picture.return_value = response
        main.run('targetDir')
        service.login.assert_called_once()
        service.post_picture.assert_called_with('testPicture.jpg')
        shutil_move.assert_called_with('testPicture.jpg', 'targetDir', copy_function=shutil.copytree)
        service.logout.assert_called_once()

    @patch('shutil.move')
    def test_Main_whenUnprocessableEntity(self, shutil_move):
        service = Mock()
        pictures = ['testPicture.jpg']
        main = Main(service, pictures, False)
        service.post_picture.return_value = Response.UNPROCESSABLE_ENTITY
        main.run('targetDir')
        service.login.assert_called_once()
        service.post_picture.assert_called_with('testPicture.jpg')
        shutil_move.assert_called_with('testPicture.jpg', 'targetDir', copy_function=shutil.copytree)
        service.logout.assert_called_once()

    def createPicture(self, name):
        picture = os.path.join(self.test_dir, name)
        f = open(picture, 'w')
        f.write('This is a kind of picture')
        f.close()
        return picture


if __name__ == '__main__':
    unittest.main()
