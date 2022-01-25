'''
Module to handle MSDTMP config files
'''
import numpy as np


class msd():
    """Class relating to MSD data

    :param source: File to read
    """

    def __init__(self, source=None):
        self.nFrames = 0
        self.nAtoms = 0
        self.data = None
        self.latom = []
        self.timestep = 0
        self.step = None
        self.time = None
        self.title = ""
        self.species = None
        self.nspecies = property(lambda self: len(self.species))

        if source is not None:
            self.source = source
            self.read(source)

    def per_specie(self):
        """List by species

        :returns: List of species averages
        :rtype: np.ndarray

        """
        self.species = list(set(self.latom))
        d = np.zeros((self.nFrames, len(self.species), 2))
        for i in range(self.nFrames):
            for j, s in enumerate(self.species):
                m = list(map(lambda x: x == s, self.latom))
                d[i, j, 0] = np.average(self.data[i, m, 0])
                d[i, j, 1] = np.average(self.data[i, m, 1])
        return d

    def read(self, filename="MSDTMP"):
        """Read an MSDTMP file

        :param filename: File to read

        """

        try:
            fileIn = open(filename, 'r')
        except IOError:
            print('File {0:s} does not exist!'.format(filename))
            return []

        self.title = fileIn.readline().strip()
        self.nAtoms, self.nFrames, _ = map(int, fileIn.readline().strip().split())
        self.data = np.zeros((self.nFrames, self.nAtoms, 2))
        self.step = np.zeros(self.nFrames)
        self.time = np.zeros(self.nFrames)
        for i in range(self.nFrames):
            d = fileIn.readline().strip().split()
            self.step[i] = int(d[1])
            self.timestep = float(d[3])
            self.time[i] = float(d[4])
            for j in range(self.nAtoms):
                if i > 0:
                    _, _, m, t = fileIn.readline().strip().split()
                    self.data[i, j, :] = float(m)**2, float(t)
                else:
                    s, _, m, t = fileIn.readline().strip().split()
                    self.data[i, j, :] = float(m)**2, float(t)
                    self.latom.append(s)

        fileIn.close()
        return self


if __name__ == '__main__':
    MSD = msd().read()
    print("number of frames {} ".format(MSD.nFrames))
