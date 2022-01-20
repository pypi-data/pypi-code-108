import os

import matplotlib.pyplot as plt

from SPMUtil.flatten import *


class BaseAnalyzer:


    def __init__(self, directory, fileNamesList=None):
        self.directory = directory
        self.directory_out = self.directory + '/AnalyzerOutputs/'
        self.fileNamesList = fileNamesList

        self.exts = []


        if not os.path.exists(self.directory_out):
            os.mkdir(self.directory_out)


    def LoadFiles(self, searchAllDirectory=True):
        if not searchAllDirectory:
            if len(self.fileNamesList) == 0:
                print("Length of File Name List is 0")
                exit(0)
            for fileName in self.fileNamesList:
                self._LoadFile(fileName)
        else:
            files = [file for file in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, file))]
            for fileName in files:
                extension = os.path.splitext(fileName)[1]
                if extension in self.exts:
                    self._LoadFile(fileName)


    def _LoadFile(self, fileName):
        raise NotImplementedError()


    @staticmethod
    def save_texture(map_2d: np.ndarray, name="texture", dir=""):
        size = map_2d.shape
        print("Texture Size", size)
        image = np.zeros((size[0], size[1], 3), np.uint8)

        maxDepth = np.max(map_2d)
        minDepth = np.min(map_2d)

        map_2d = (map_2d - minDepth) / (maxDepth - minDepth) * 255

        for i in range(0, size[1]):
            for j in range(0, size[0]):
                image.itemset((j, i, 0), map_2d[j, i])
                image.itemset((j, i, 1), map_2d[j, i])
                image.itemset((j, i, 2), map_2d[j, i])

        plt.imshow(image)
        plt.savefig(os.path.join(dir, name + '.png'))

