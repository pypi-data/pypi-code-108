import unittest
import tempfile
import shutil

from dslibrary.utils.file_utils import FileOpener, connect_to_filesystem, write_stream_with_read_on_close


class TestFileUtils(unittest.TestCase):

    def test_FileOpener_local_file(self):
        tmp_f = tempfile.mkdtemp()
        fo = FileOpener(tmp_f)
        with fo.open("x", mode="w") as f_w:
            f_w.write("abc")
        with fo.open("x", mode="r") as f_r:
            self.assertEqual(f_r.read(), "abc")
        shutil.rmtree(tmp_f)

    def test_write_stream_with_read_on_close(self):
        log = []
        f_w = write_stream_with_read_on_close('w', 'r', on_close=lambda fh: log.append(fh.read()))
        f_w.write("abc")
        f_w.write("def")
        f_w.close()
        assert log == ["abcdef"]

    def test_connect_to_filesystem(self):
        tmp_f = tempfile.mkdtemp()
        fs = connect_to_filesystem(tmp_f, for_write=True)
        with fs.open("x", mode="w") as f_w:
            f_w.write("abc")
        with fs.open("x", mode="r") as f_r:
            self.assertEqual(f_r.read(), "abc")
        self.assertEqual(fs.ls(), [{'name': 'x', 'size': 3, 'type': 'file'}])
        self.assertEqual(fs.stat("x"), {'name': 'x', 'size': 3, 'type': 'file'})
        assert fs.exists("x") is True
        assert fs.exists("y") is False
        shutil.rmtree(tmp_f)
