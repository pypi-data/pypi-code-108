import nanonispy as nap

import SPMUtil as spmu
from SPMUtil.analyzer.BaseAnalyzer import *


class SxmAnalyzer(BaseAnalyzer):

    class AnalyzeMode(Enum):
        Z = 1
        NanoSurf = 2
        Nanosurf_Amplitude = 3
        Nanosurf_Dissipation = 4
        Current = 5
        Phase = 6
        Amplitude = 7
        Frequency_Shift = 8
        Excitation = 9

    def __init__(self, directory, fileNamesList=None):
        super(SxmAnalyzer, self).__init__(directory, fileNamesList)
        self.analyzeMode = self.AnalyzeMode.Z

    def SaveTextureFiles(self, analyzeMode=AnalyzeMode(1), searchAllDirectory=True):
        self.analyzeMode = analyzeMode
        if not searchAllDirectory:
            if len(self.fileNamesList) == 0:
                print("Length of File Name List is 0")
                exit(0)
            for fileName in self.fileNamesList:
                self._LoadFile(fileName, 'forward')
                self._LoadFile(fileName, 'backward')
        else:
            files = [file for file in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, file))]
            for it in files:
                extension = os.path.splitext(it)[1]
                if extension == '.sxm':
                    self._LoadFile(os.path.splitext(it)[0], 'forward')
                    self._LoadFile(os.path.splitext(it)[0], 'backward')

    def _LoadFile(self, fileName, secondKey='forward'):

        file_path = os.path.join(self.directory, fileName + ".sxm")

        file = nap.read.Scan(file_path)
        if file is None:
            print(fileName + "File Not Exist")
            exit(0)


        data_size = (file.header['scan_pixels'][0], file.header['scan_pixels'][1])
        map_data = np.array(file.signals[self.analyzeMode.name][secondKey]).reshape(shape=data_size)

        self.save_texture(spmu.flatten_map(map_data), dir=self.directory_out,
                            name=fileName + "_" + self.analyzeMode.name + "_" + secondKey)