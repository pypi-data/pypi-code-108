import nanonispy as nap

import SPMUtil as spmu
import SPMUtil.formula as formula
from SPMUtil.analyzer.BaseAnalyzer import *


class GridAnalyzer(BaseAnalyzer):

    def __init__(self, directory, fileNamesList=None, **kwargs):
        super(GridAnalyzer, self).__init__(directory, fileNamesList)

        self.fileDict = {}
        self._topo_cache = {}
        self.topo_flatten_mode = FlattenMode.PolyFit
        self.topo_apply_smooth = True
        self._custom_topo = None
        self._custom_3darray = None
        self.exts = [".3ds"]

        BaseAnalyzer.topo_poly_order = 3
        BaseAnalyzer.gaussian_filter_sigma = 0.5

        if "topo_flatten_mode" in kwargs:
            self.topo_flatten_mode = kwargs["topo_flatten_mode"]
        if "topo_apply_smooth" in kwargs:
            self.topo_apply_smooth = kwargs["topo_apply_smooth"]
        if "topo_poly_order" in kwargs:
            BaseAnalyzer.topo_poly_order = kwargs["topo_poly_order"]
        if "gaussian_filter_sigma" in kwargs:
            BaseAnalyzer.gaussian_filter_sigma = kwargs["gaussian_filter_sigma"]
        if "custom_topo" in kwargs:
            self._custom_topo = kwargs["custom_topo"]
        if "custom_3darray" in kwargs:
            self._custom_3darray = kwargs["custom_3darray"]


    def get_curve(self, point=(0, 0), fileName=None):
        if fileName is None and len(self.fileDict.values()) > 0:
            fileName = list(self.fileDict.keys())[0]
        elif fileName not in self.fileDict:
            raise ValueError("fileName error")

        # xy = self.get_xy_count(fileName)
        if self._custom_3darray is None:
            y = self.fileDict[fileName].signals["Frequency Shift (Hz)"][point[1], point[0], :]
        else:
            y = self._custom_3darray[point[1], point[0], :]
        return self.__get_xdata(self.fileDict[fileName], point, self.topo(fileName)), y

    def get_data_count(self, fileName):
        return self.fileDict[fileName].header["num_sweep_signal"]

    def get_xy_count(self, fileName):
        return self.fileDict[fileName].header["dim_px"]

    def get_height_range(self, fileName):
        minValue = 999
        maxValue = 0
        for i in range(0, self.get_xy_count(fileName)[0]):
            for j in range(0, self.get_xy_count(fileName)[1]):
                x, y = self.get_curve((i, j), fileName)
                if np.min(x) < minValue:
                    minValue = np.min(x)
                if np.max(x) > maxValue:
                    maxValue = np.max(x)
        return minValue - np.min(self.topo(fileName)), maxValue - np.min(self.topo(fileName))

    @staticmethod
    def __get_xdata(file, point, topo):
        # print(np.min(file.signals["topo"]), np.max(file.signals["topo"]))
        data_num = file.header["num_sweep_signal"]
        param = file.signals["params"][point[1], point[0], :]
        # print(param[0], param[1], param[4])
        x = np.linspace(param[0], param[1], data_num) + topo[point[1]][point[0]]

        x -= np.min(topo)
        return x * 10 ** 10

    def get_df_matrix(self, fileName):
        if self._custom_3darray is None:
            return self.fileDict[fileName].signals["Frequency Shift (Hz)"]
        else:
            return self._custom_3darray

    def topo(self, fileName):
        if self._custom_topo is not None:
            return self._custom_topo

        if fileName not in self._topo_cache:
            self._topo_cache[fileName] = flatten_map(self.fileDict[fileName].signals["topo"],
                                                          flatten=self.topo_flatten_mode)
            # return self.fileDict[fileName].signals["topo"]
        return self._topo_cache[fileName]

    def CalcFMap(self, fileName, param: spmu.structures.measurement_param, save_path):
        cvt = spmu.converter.PakConvertor(fileName, save_path, False)

        xy = self.get_xy_count(fileName)
        header = spmu.converter.PakConvertor.PakHeader(data_size=xy, data_count=self.get_data_count(fileName))
        header.comment = "3D force map, Calculate by GridAnalyzer"
        cvt.set_header(header)
        for i in range(0, xy[0]):
            for j in range(0, xy[1]):
                x, y = self.get_curve(point=(i, j), fileName=fileName)
                x = np.flipud(x)
                y = np.flipud(y)
                f = formula.CalcForceCurveSadar(y, param)
                cvt.add_data((i,j), spmu.structures.force_curve(x=x, y=f))

                print("finished", (i, j), "/", xy)
        cvt.save()

    def _LoadFile(self, fileName):
        file_path = os.path.join(self.directory, fileName)
        file = nap.read.Grid(file_path)
        if file is None:
            print(fileName + "File Not Exist")
            exit(0)
        print(fileName)
        # print(file.signals["Frequency Shift (Hz)"].shape)
        # print(file.header)
        self.fileDict[fileName] = file

