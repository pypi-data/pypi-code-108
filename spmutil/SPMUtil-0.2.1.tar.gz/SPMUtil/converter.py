import os

import numpy as np

import SPMUtil as spmu
from .DataSerializer import DataSerializer


class BaseConvertor:
    def __init__(self, fileName="", data_path="", openFile=True):
        self.fileName = fileName
        self.path = os.path.abspath(os.path.join(data_path, fileName)).replace(os.sep, "/")
        if openFile:
            self.file = open(self.path)
        self._pdata = None

    @property
    def pdata(self):
        raise NotImplementedError()

    def reconstruct_map(self):
        return np.array(self.pdata)

    def get_y_data(self, index=1):
        # print("get y data," + str(index))
        data = self.pdata.values
        return np.array(data[:, index])

    def get_x_data(self, offset=0):
        x = self.get_y_data(0)
        if offset == "auto":
            x -= min(x)
        elif offset is not None:
            x = x - offset
        return x


class GridConvertor(BaseConvertor):

    def __init__(self, fileName="", data_path=""):
        BaseConvertor.__init__(self, fileName, data_path)
        self.analyzer = spmu.analyzer.GridAnalyzer(data_path, fileNamesList=[fileName])
        self.analyzer.LoadFiles(searchAllDirectory=False)

    def get_x_data(self, point=(0,0), offset=None):
        x, y = self.analyzer.get_curve(fileName=self.fileName, point=point)
        if offset == "auto":
            x -= min(x)
        elif offset is None:
            x -= np.min(self.analyzer.topo(self.fileName))
        elif offset is not None:
            x = x - offset
        return np.flipud(x)

    def get_y_data(self, point=(0,0)):
        x, y = self.analyzer.get_curve(fileName=self.fileName, point=point)
        return np.flipud(y)

    @property
    def pdata(self):
        return None



"""
    The custom data pack will save in this class
    It has save and load interface
    save will be a dict, use key to carry out data
"""




class PakConvertor(BaseConvertor):

    class PakHeader:
        def __init__(self, data_size, data_count):
            self.data_size = data_size
            self.data_count = data_count
            self.comment = "none"
            self.f0 = None
            self.amp = None
            self.k = None

    def __init__(self, fileName="", data_path="", autoLoad=True):
        BaseConvertor.__init__(self, fileName, data_path, False)
        self.data = DataSerializer(self.path)
        if autoLoad:
            self.data.load()

    def get_x_data(self, point=(0,0), offset=None):
        x = self.data.data_dict[point].x
        if offset == "auto":
            x -= min(x)
        elif offset is None:
            pass
        elif offset is not None:
            x = x - offset
        return np.array(x)

    def get_y_data(self, point=(0,0)):
        y = self.data.data_dict[point].y
        return np.array(y)

    def set_header(self, header):
        self.data.set_header(header)

    def add_data(self, key, data, overwrite=False):
        self.data.add_data(key, data, overwrite)

    def save(self):
        self.data.save()

    def load(self):
        self.data.load()

    @property
    def pdata(self):
        return None

    def reconstruct_map(self):
        size = self.data.header.data_size
        if type(size) is not int and len(size) == 2:
            map = np.zeros(shape=(size[0], size[1], self.data.header.data_count))
            for i in range(size[0]):
                for j in range(size[1]):
                    map[j, i, :] = self.data.data_dict[(i, j)].y

        if type(size) is int:
            map = np.zeros(shape=(size, self.data.header.data_count))
            for i in range(1, size+1):
                    map[:, i-1] = self.data.data_dict[i].y
        else:
            raise NotImplementedError()
        return map


if __name__ == "__main__":
    pak = PakConvertor("Si_H_0041.f.ch1")

