import unittest
import tempfile
import pathlib
import os

from fsos import bucket_manager as bm


class BMTests(unittest.TestCase):
    def test_bucket_manage(self):
        temp_dir = str(pathlib.Path(pathlib.Path.home(), ".fsos"))
        TEST_BUCKET_NAME = "test_bucket"
        bm.make_bucket(TEST_BUCKET_NAME)
        self.assertEqual(pathlib.Path(
            temp_dir, TEST_BUCKET_NAME).exists(), True)

        self.assertEqual(bm.bucket_exists(
            TEST_BUCKET_NAME), True)

        self.assertEqual(bm.bucket_list(), [TEST_BUCKET_NAME])

        bm.remove_bucket(TEST_BUCKET_NAME)
        self.assertEqual(pathlib.Path(
            temp_dir, TEST_BUCKET_NAME).exists(), False)

        pathlib.Path(temp_dir, ".fsos").unlink()
        pathlib.Path(temp_dir).rmdir()

    def test_bucket_manage_custom_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            TEST_BUCKET_NAME = "test_bucket"
            bm.make_bucket(TEST_BUCKET_NAME, temp_dir)
            self.assertEqual(pathlib.Path(
                temp_dir, TEST_BUCKET_NAME).exists(), True)

            self.assertEqual(bm.bucket_exists(
                TEST_BUCKET_NAME, temp_dir), True)

            self.assertEqual(bm.bucket_list(temp_dir), [TEST_BUCKET_NAME])

            bm.remove_bucket(TEST_BUCKET_NAME, temp_dir)
            self.assertEqual(pathlib.Path(
                temp_dir, TEST_BUCKET_NAME).exists(), False)

    def test_file_manage(self):
        # Windows bug for TemporaryFile access - https://stackoverflow.com/questions/23212435/permission-denied-to-write-to-my-temporary-file
        # temp_file = tempfile.NamedTemporaryFile(mode='w')
        temp_file = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        open(temp_file, "x").close()
        # with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = str(pathlib.Path(pathlib.Path.home(), ".fsos"))
        TEST_BUCKET_NAME = "test_bucket"
        TEST_OBJECT_NAME = "test_object"
        bm.make_bucket(TEST_BUCKET_NAME)
        bm.put_filepath(TEST_BUCKET_NAME, TEST_OBJECT_NAME,
                        temp_file, meta_info={"cls": [1, 2]})
        self.assertEqual(pathlib.Path(
            temp_dir, TEST_BUCKET_NAME, TEST_OBJECT_NAME).exists(), True)
        self.assertEqual(bm.get_filepaths(TEST_BUCKET_NAME, temp_dir), [
            pathlib.Path(temp_dir, f"{TEST_BUCKET_NAME}/{TEST_OBJECT_NAME}")])

        bm.remove_object(TEST_BUCKET_NAME, TEST_OBJECT_NAME)
        bm.remove_bucket(TEST_BUCKET_NAME)

        pathlib.Path(temp_file).unlink()

        pathlib.Path(temp_dir, ".fsos").unlink()
        pathlib.Path(temp_dir).rmdir()


if __name__ == "__main__":
    unittest.main()
