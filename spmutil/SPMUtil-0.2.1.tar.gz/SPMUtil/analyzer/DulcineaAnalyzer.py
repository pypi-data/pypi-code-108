# from SPMUtil.analyzer.BaseAnalyzer import *
# import SPMUtil as spmu
# import pandas as pd
#
# class DulcineaAnalyzer(BaseAnalyzer):
#     """""""""""""""""
#     Note:
#         top: Topography
#         ch1: df
#         ch2: Amplitude
#         ch3: Dissipation
#         ch4: Current
#
#     """""""""""""""""
#     def __init__(self, directory, fileNamesList=None):
#         super(DulcineaAnalyzer, self).__init__(directory, fileNamesList)
#         self.exts = ["top", "ch1"]
#
#     def __SaveFile(self, fileName, doFitting=True, saveFile=True):
#
#         def get_value(key: str):
#             value = [x for x in header if x.find(key) != -1]
#             if len(value) > 0:
#                 return value[0].split(":")[1]
#             else:
#                 return None
#
#         file_path = os.path.join(self.directory, fileName)
#         print("Opening " + fileName + " ================================")
#
#         with open(file_path, 'rb') as f:
#             file = f.read().split(b'[Header end]')
#             header = str(file[0]).replace(" ", "").split('\\r\\n')
#             content = file[1]
#
#             data_list = np.frombuffer(content, dtype='<h')
#             # print(len(data_list)-1)
#             """
#                 binaryデータの変換について
#                     short型で読み込んで単位はm voltage(mV)です。
#                     short型の32767は10V に対応します。
#
#                     voltageから周波数シフトに変換するとき　72.24 Hz/V のPLLを使っています.
#
#                     20180906以前のマッピングデータはshort型で出力しているので
#                     ㎐ に変換する時　/ 3.2767  * 72.24 / 1000　の倍数関係を利用する
#
#             """
#             # V
#             data_list = data_list[1:] / 3.2767 / 1000
#             data_size = int(get_value("Numberofcolumns")), int(get_value("Numberofrows"))
#
#             rowIndex = 0
#             columnIndex = 0
#             pixel_data = []
#
#             for data in data_list:
#                 pixel_data.append(Vector3(data_size[1] - columnIndex - 1, data_size[0] - rowIndex - 1, data))
#
#                 rowIndex += 1
#                 if rowIndex == data_size[1]:
#                     rowIndex = 0
#                     columnIndex += 1
#                     if columnIndex >= data_size[1]:
#                         break
#         if doFitting:
#             pixel_data = self.fitting_data(pixel_data, data_size)
#
#         if saveFile:
#             self.save_texture(pixel_data, data_size, dir=self.directory_out, name=fileName)
#
#         return pixel_data, data_size, header
#
#     def GetDfMap(self, fileName, N=1, saveFile=False):
#         result = self.__SaveFile(fileName, False)
#         # print(result[2])
#
#         def get_value(key: str):
#             value = [x for x in result[2] if x.find(key) != -1]
#             if len(value) > 0:
#                 return value[0].split(":")[1]
#             else:
#                 return None
#
#         if "\\xc5" in get_value("YAmplitude"):
#             height_amp = float(get_value("YAmplitude").replace("\\xc5", "")) * 40.9 * 0.1
#         elif "nm" in get_value("YAmplitude"):
#             height_amp = float(get_value("YAmplitude").replace("nm", "")) * 40.9
#         else:
#             raise ValueError("Can not read YAmplitude unit in header")
#         print("height", height_amp)
#         data = np.zeros(shape=(result[1].x, result[1].y))
#         for it in result[0]:
#             # data[it.x][it.y] = (it.z - minDepth) / (maxDepth - minDepth) * -1
#             data[it.x][it.y] = it.z
#
#         mapper = DulcineaMapCreator()
#         mapper.N = N
#         data = mapper.CalcDfsMap(data)
#         # plt.imshow(data)
#         # plt.colorbar()
#         # plt.show()
#         index = np.zeros(shape=result[1].x)
#         for i in range(0, result[1].x):
#             index[i] = i / result[1].x * height_amp
#
#         if saveFile:
#             pd.DataFrame(data, index=index).to_csv(fsh.default_data_path + fileName + ".csv")
#             pak = spmu.converter.PakConvertor(fileName, fsh.default_project_path, autoLoad=False)
#             for i in range(1, 1025):
#                 pak.add_data(i, spmu.structures.force_curve(temp.get_x_data(i), temp.get_y_data(i)))
#
#             header = spmu.converter.PakConvertor.PakHeader(data_size=result[1].x, data_count=result[1].y)
#             pak.set_header(header)
#             pak.save()
#             del pak
#             os.remove(fsh.default_data_path + fileName + ".csv")
#
#         return data, index
#
#     def GetMap(self, fileName):
#         if len(self.fileNamesList) == 0 or fileName not in self.fileNamesList:
#             print("Length of FileNameList is 0 or error fileName in FileNameList")
#             exit(0)
#         extension = os.path.splitext(fileName)[1]
#         if extension == '.top':
#             pixel_data, size, _ = self.__SaveFile(fileName, True, False)
#         elif extension.find("ch") != -1:
#             pixel_data, size, _ = self.__SaveFile(fileName, False, False)
#         else:
#             raise ValueError()
#         image = np.zeros((size.x, size.y))
#         maxDepth = sys.float_info.min
#         minDepth = sys.float_info.max
#         for it in pixel_data:
#             if it.z > maxDepth:
#                 maxDepth = it.z
#             if it.z < minDepth:
#                 minDepth = it.z
#         for v in pixel_data:
#             color = (v.z - minDepth) / (maxDepth - minDepth) * 255
#             image[v.x, v.y] = color
#         return image
#
#     def CalcFMap(self, fileName, saveFileName, f0, amp, k, N=1, method="sadar", useFilter=False, filterWindowSize=31):
#         result = self.__SaveFile(fileName, False)
#
#         def get_value(key: str):
#             value = [x for x in result[2] if x.find(key) != -1]
#             if len(value) > 0:
#                 return value[0].split(":")[1]
#             else:
#                 return None
#         height_amp = float(get_value("YAmplitude").replace("\\xc5", "").replace("nm", "")) * 40.9 * 0.1
#
#         index = np.zeros(shape=result[1].x)
#         for i in range(0, result[1].x):
#             index[i] = i / result[1].x * height_amp
#
#         param = spmu.structures.measurement_param(height_amp, result[1].y)
#         param.amp = amp
#         param.f0 = f0
#         param.k = k
#
#         cvt = spmu.converter.PakConvertor(saveFileName, autoLoad=False)
#         header = spmu.converter.PakConvertor.PakHeader(data_size=result[1].x, data_count=result[1].y)
#         header.f0 = f0
#         header.amp = amp
#         header.k = k
#         header.comment = "2D force map, Calculate by DulcineaAnalyzer"
#         cvt.set_header(header)
#
#         map, x = self.GetDfMap(fileName, N=N)
#         for i in range(0, 1024):
#                 y = map[:, i]
#                 if useFilter:
#                     y = spmu.filter_1d.savitzky_golay_fliter(y, filterWindowSize)
#
#                 if method == "sadar":
#                     f = spmu.formula.CalcForceCurveMatrix(y, param)
#                 elif method == "matrix":
#                     f = spmu.formula.CalcForceCurveSadar(y, param)
#                 else:
#                     raise ValueError("no known method")
#
#                 # plt.clf()
#                 # plt.axhline(y=0, c="black")
#                 # plt.plot(x, formula.CalcForceCurveMatrix(y, param), c="b")
#                 # plt.plot(x, formula.CalcForceCurveSadar(y, param), c="r")
#                 # plt.show()
#                 cvt.add_data((i), spmu.structures.force_curve(x=x, y=f))
#                 print("finished", i, "/", 1024)
#         cvt.save()
#
#     def SmoothFMap(self, fileName, f_path, method="ave", method_param=20):
#         result = self.__SaveFile(fileName, False)
#
#         def get_value(key: str):
#             value = [x for x in result[2] if x.find(key) != -1]
#             if len(value) > 0:
#                 return value[0].split(":")[1]
#             else:
#                 return None
#
#         height_amp = float(get_value("YAmplitude").replace("\\xc5", "")) * 40.9 * 0.1
#         index = np.zeros(shape=result[1].x)
#         for i in range(0, result[1].x):
#             index[i] = i / result[1].x * height_amp
#
#         data = np.asarray(pd.read_csv(f_path).values)[:, 1:]
#         if method == "ave":
#             F = spmu.filter_2d.SmoothMap(data, method_param)
#         elif method == "fft":
#             F = spmu.filter_2d.FFTMap_LowPass(data, method_param)
#         elif method == "fft2":
#             F = spmu.filter_2d.FFT2Map_LowPass(data, method_param)
#         else:
#             print("SmoothFMap method error")
#             return
#         pd.DataFrame(F, index=index).to_csv("Force_smooth-" + method + ".csv")
