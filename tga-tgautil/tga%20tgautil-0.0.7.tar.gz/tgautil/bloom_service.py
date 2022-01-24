import os.path
import time
from config.settings import DATA_BASE
from pybloom_live import ScalableBloomFilter


def ensure_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


class BloomDeduplicate:
    # 转发表的ID
    def __init__(self, forward_id):
        self.forward_id = forward_id
        bloom_path = os.path.join(DATA_BASE, 'bloom')
        ensure_path(bloom_path)
        self.file_path = os.path.join(bloom_path, "forward_" + str(forward_id) + '.bloom')
        if not os.path.isfile(self.file_path):
            self.bloom = ScalableBloomFilter(initial_capacity=10000, error_rate=0.001)
        else:
            self.f = open(self.file_path, "rb")
            self.bloom = ScalableBloomFilter.fromfile(open(self.file_path, "rb"))
        self.wf = open(self.file_path, "wb")

    # True 代表已经转发过
    def is_exist(self, item):
        result = False
        if item in self.bloom:
            result = True
        else:
            self.bloom.add(item)
        return result

    def __del__(self):
        self.bloom.tofile(self.wf)


if __name__ == "__main__":
    bd = BloomDeduplicate("1")
    start = time.time()
    for i in range(0, 2000):
        if not bd.is_exist(10000 + i):
            print("error----")

        if i % 100000 == 0:
            print(i, time.time() - start, "||||||||")
