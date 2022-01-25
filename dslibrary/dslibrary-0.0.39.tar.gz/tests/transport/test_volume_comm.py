"""
Using to_volume and volume_watcher.
"""
import unittest
import tempfile
import threading
import shutil

from dslibrary.transport.to_local import DSLibraryLocal
from dslibrary.transport.to_volume import DSLibraryViaVolume
from dslibrary.transport.volume_watcher import VolumeWatcher


class TestVolumeComm(unittest.TestCase):

    def vol_to_vol_setup(self):
        class Setup(object):
            def __enter__(self):
                self.volume = tempfile.mkdtemp()
                self.target_data = tempfile.mkdtemp()
                self.front = DSLibraryViaVolume(self.volume)
                self.target = DSLibraryLocal(self.target_data)
                self.xfer = VolumeWatcher(self.volume, self.target)
                # bg thread to manage 'xfer'
                self.done = []
                def my_callback():
                    if self.done:
                        raise StopIteration
                self.bg = threading.Thread(target=lambda: self.xfer.scan_forever(callback=my_callback))
                self.bg.start()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.done.append(1)
                shutil.rmtree(self.volume)
                shutil.rmtree(self.target_data)
                self.bg.join()
        return Setup()

    def test_file_rw(self):
        with self.vol_to_vol_setup() as env:
            # read data from target
            env.target.write_resource("file1", "DATA1")
            self.assertEqual(env.front.read_resource("file1", mode='r'), "DATA1")
            self.assertEqual(env.front.read_resource("file1", mode='rb'), b"DATA1")
            env.target.write_resource("file1", b"DATA1")
            self.assertEqual(env.front.read_resource("file1", mode='r'), "DATA1")
            self.assertEqual(env.front.read_resource("file1", mode='rb'), b"DATA1")
            # write data to target
            env.front.write_resource("file2", "DATA2")
            self.assertEqual(env.target.read_resource("file2", 'r'), "DATA2")
            self.assertEqual(env.target.read_resource("file2", 'rb'), b"DATA2")
            env.front.write_resource("file2", b"DATA2")
            self.assertEqual(env.target.read_resource("file2", 'r'), "DATA2")
            self.assertEqual(env.target.read_resource("file2", 'rb'), b"DATA2")
