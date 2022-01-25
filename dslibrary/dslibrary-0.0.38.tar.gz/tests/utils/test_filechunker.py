import unittest
import random
import os
import pandas
from pandas.core.dtypes.inference import is_file_like

from dslibrary.utils.filechunker import ChunkedFileReader, ChunkedFileWriter


class TestFileChunkers(unittest.TestCase):

    def test_rd(self):
        data = "1234567890"
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        assert f.name == "x"
        assert f.read(3) == "123"
        assert f.read() == "4567890"
        f.seek(1)
        assert f.read(4) == "2345"
        f.close()

    def test_rd_b(self):
        data = b"1234567890"
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='rb')
        assert f.name == "x"
        assert f.read(3) == b"123"
        assert f.read() == b"4567890"
        f.seek(1)
        assert f.read(4) == b"2345"
        f.close()

    def test_rd_minChunk(self):
        data = "1234567890"
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        f._min_chunk = 4
        assert f.read(3) == "123"
        assert f._chunk == "1234"
        assert f._offset == 3
        assert f._pos == 3
        assert f.read(2) == "45"
        assert f._chunk == "5678"
        assert f._offset == 1
        assert f._pos == 5
        f.seek(6)
        assert f._offset == 2
        assert f._pos == 6
        assert f.read(2) == "78"

    def test_seek_misc(self):
        data = "1234567890"
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        assert f.read(3) == "123"
        assert f.tell() == 3
        f.seek(2)
        assert f.tell() == 2
        assert f.read(3) == "345"
        assert f.tell() == 5
        f.seek(1, 1)
        assert f.tell() == 6
        assert f.read() == "7890"
        f.seek(-2, 2)
        assert f.tell() == 8
        assert f.read() == "90"
        assert f.tell() == 10

    def test_seek_from_end(self):
        data = "1234567890"
        for mode in ["constant", "function", "unknown"]:
            f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r', size=10 if mode == "constant" else lambda: 10 if mode == "function" else None)
            if mode == "unknown":
                self.assertRaises(Exception, lambda: f.seek(0, 2))
                continue
            f.seek(0, 2)
            assert f.tell() == 10
            f.seek(0, 0)
            f.seek(-2, 2)
            assert f.tell() == 8
            assert f.read() == "90"
            assert f.tell() == 10

    def test_rd_max_read(self):
        data = "x"*200
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        f._max_read = 100
        assert f.read() == "x"*100
        assert f.read() == "x"*100
        assert f.read() == ""

    def test_rd_direct(self):
        data = "x"*100
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        assert f.read() == "x"*100

    def test_rd_fix_type(self):
        data = "1234567890"
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='rb')
        assert f.read(3) == b"123"
        data = b"1234567890"
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        assert f.read(3) == "123"

    def test_rd_lines(self):
        data = "a\nb\nc\nd"
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        rr = list(f)
        assert rr == ["a", "b", "c", "d"]

    def test_wr_misc(self):
        out = ['x']
        def wr(data, append):
            if not append:
                out[0] = ""
            out[0] += data
        f = ChunkedFileWriter("name", wr, mode='w')
        assert f.name == "name"
        f.write("a")
        f.write("b")
        f.flush()
        f.close()
        assert out == ["ab"]

    def test_wr_append(self):
        out = ['x']
        def wr(data, append):
            if not append:
                out[0] = ""
            out[0] += data
        f = ChunkedFileWriter("name", wr, mode='wa')
        assert f.name == "name"
        f.write("a")
        f.write("b")
        f.close()
        assert out == ["xab"]

    def test_wr_mpu(self):
        """
        Write with multi-part-upload hints.
        """
        log = []
        def wr(data, append, hint):
            log.append((data, append, hint))
            if hint.startswith("start"):
                return "UUU"
        f = ChunkedFileWriter("name", wr, mode='w', chunk_size=100)
        assert f.name == "name"
        f.write("a"*80)
        f.write("b"*80)
        f.close()
        assert log[0] == ("a"*80 + "b"*20, False, "start:-1")
        assert log[1] == ("b"*60, True, "end:UUU:1")

    def test_wr_mpu_1(self):
        """
        Write with multi-part-upload hints.
        """
        log = []
        def wr(data, append, hint=None):
            log.append((data, append, hint))
            if hint == "start":
                return "UUU"
        f = ChunkedFileWriter("name", wr, mode='w', chunk_size=100)
        assert f.name == "name"
        f.write("a"*80)
        f.close()
        assert log[0] == ("a"*80, False, None)

    def test_random_lines(self):
        lengths = [random.randint(0, 40) for _ in range(1000)]
        out = []
        with ChunkedFileWriter("", lambda data, append: out.append(data), chunk_size=101) as wr:
            for n, ll in enumerate(lengths):
                ch = chr(ord("0") + (n % 9))
                wr.write(ch*ll + "\n")
        raw = "".join(out)
        rd = ChunkedFileReader("", lambda a, b: raw[a:b], chunk_size=100)
        l_out = [len(line) for line in rd]
        assert l_out == lengths

    def test_post_slice(self):
        data = "a\nb\nc\nd"
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        assert list(f[:2]) == ["a", "b"]
        f.seek(0)
        assert list(f[2:]) == ["c", "d"]
        f.seek(0)
        assert list(f[::2]) == ["a", "c"]
        self.assertRaises(Exception, lambda: list(f[-2:]))
        self.assertRaises(Exception, lambda: list(f[0:-2]))
        self.assertRaises(Exception, lambda: list(f[0:1:-1]))

    def test_eof_issue(self):
        data = 'x' * 100
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        assert len(f.read(1000)) == 100
        d = f.read(1000)
        assert not d and f._eof
        d = f.read(1000)
        assert not d and f._eof

    def test_pandas_ok(self):
        data = 'x' * 100
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='r')
        assert is_file_like(f)

    def test_pandas_ok2(self):
        data = 'x,y\n1,10\n2,20'
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='rb')
        df = pandas.read_csv(f)
        assert list(df.columns) == ["x", "y"]

    def test_pandas_ok3(self):
        fn = os.path.join(os.path.dirname(__file__), "../test_data/two_cols.xlsx")
        with open(fn, 'rb') as f:
            data = f.read()
        f = ChunkedFileReader("x", lambda a, b: data[a:b], mode='rb', size=len(data))
        df = pandas.read_excel(f, engine="openpyxl")
        assert list(df.columns) == ["a", "b"]

    def test_capabilities(self):
        f = ChunkedFileReader("x", lambda a, b: "", mode='r')
        assert f.readable() is True
        assert f.writable() is False
        assert f.seekable() is True
        def wr(data, append):
            pass
        f = ChunkedFileWriter("name", wr, mode='w')
        assert f.writable() is True
        assert f.readable() is False
        assert f.seekable() is False
