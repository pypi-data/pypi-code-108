""" Module containing data related to parsing output """
import numpy as np


class Output():
    """Class containing parsed OUTPUT data

     :param source: OUTPUT file to read

     """
    __version__ = "0"

    def __init__(self, source=None):

        self.vdwEnergy = None
        self.vdwPressure = None
        self.steps = None
        self.averageSteps = None
        self.time = None  # in ps
        self.averageTime = None
        self.runTime = None
        self.runTps = None
        self.average = None
        self.pressure = None
        self.pressureTensor = None
        self.pressureTensorRms = None
        self.averageCell = None
        self.averageCellRms = None
        self.diffusion = None

        if source is not None:
            self.source = source
            self.read(source)

    @staticmethod
    def type_3x3(label, a):
        """Print as 3x3 block

        :param label: Label to print
        :param a: Value stored

        """
        out = "{}: \n".format(label)
        for i in range(3):
            out += "{:16.8e} {:16.8e} {:16.8e}\n".format(a[i, 0], a[i, 1], a[i, 2])
        return out

    def __str__(self):
        outStr = ''
        if self.vdwEnergy is not None:
            outStr += "long range vdw energy correction: {} donkeys\n".format(self.vdwEnergy)
            outStr += "long range vdw pressure correction: {} donkeys\n".format(self.vdwPressure)
        outStr += "runtime for md loop: {} s\n".format(self.runTime)
        outStr += "time per md step: {} s\n".format(self.runTps)
        outStr += "md steps: {}\n".format(self.steps)
        outStr += "md steps for average: {}\n".format(self.averageSteps)
        outStr += "md simulation time: {} ps\n".format(self.time)
        outStr += "md simulation time for average: {} ps\n".format(self.averageTime)
        if self.average is not None:
            outStr += "Averages: \n"
            outStr += "#{:16s} {:>16s} {:>16s} \n".format("name", "value", "rms")
            for k, v in self.average.items():
                outStr += " {:16s} {:16.8e} {:16.8e}\n".format(k, *v)
            outStr += "\n"
        if self.diffusion is not None:
            outStr += "Approximate 3D Diffusion Coefficients and square root of MSDs:\n"
            outStr += "#{:16s} {:>20s} {:>16s} \n".format("Specie", "DC [10^-9 m^2 s^-1]", "Sqrt(MSD) [Å]")
            for k, v in self.diffusion.items():
                outStr += " {:16s}     {:16.8e} {:16.8e}\n".format(k, *v)
            outStr += "\n"
        if self.pressureTensor is not None:
            outStr += self.type_3x3("Average pressure tensor [katm]: ", self.pressureTensor)
            outStr += self.type_3x3("Average pressure tensor rms [katm]: ", self.pressureTensorRms)
            outStr += "pressure (trace/3) [katm]: {}\n".format(self.pressure)
        if self.averageCell is not None:
            outStr += self.type_3x3("Average cell vectors [Å]: ", self.averageCell)
            outStr += self.type_3x3("Average cell vectors rms [Å]: ", self.averageCellRms)
        return outStr

    def read(self, source="OUTPUT"):
        """ Read an OUTPUT file into memory

        :param source: File to read

        """
        with open(source, 'r') as f:
            line = f.readline()
            while line:
                line = f.readline()
                a = line.strip().split()
                if len(a) == 0:
                    continue
                if a[0] == 'vdw':
                    if a[1] == 'energy':
                        self.vdwEnergy = float(a[2])
                    if a[1] == 'pressure':
                        self.vdwPressure = float(a[2])
                    continue
                if a[0] == 'run':
                    self.steps = int(a[3])
                    self.time = float(a[6])
                    self.averageSteps = int(a[12])
                    self.averageTime = float(a[15])
                    dline = f.readline()
                    h = []
                    for i in range(3):
                        h += f.readline().strip().split()[1:]
                    h = h[0:18] + h[20:]
                    dline = f.readline()
                    v = []
                    for i in range(3):
                        v += [float(j) for j in f.readline().strip().split()[1:]]
                    dline = f.readline()
                    rms = []
                    for i in range(3):
                        rms += [float(j) for j in f.readline().strip().split()[1:]]
                    self.average = {l: (a, b) for (l, a, b) in zip(h, v, rms)}
                    continue
                if a[0] == 'Loop':
                    self.runTime = float(a[6])
                    self.runTps = float(a[11])
                    continue
                if a[0] == 'Pressure':
                    dline = f.readline()
                    self.pressureTensor = np.zeros((3, 3))
                    self.pressureTensorRms = np.zeros((3, 3))
                    for i in range(3):
                        a = [float(j) for j in f.readline().strip().split()]
                        self.pressureTensor[i, :] = np.array(a[0:3])
                        self.pressureTensorRms[i, :] = np.array(a[3:6])
                    self.pressure = float(f.readline().strip().split()[1])
                    continue
                if a[0] == 'Approximate':
                    dline = f.readline()
                    h = []
                    while True:
                        dline = f.readline().strip().split()
                        if len(dline) == 0:
                            break
                        h += [dline]
                    self.diffusion = {e[0]: (float(e[1]), float(e[2])) for e in h}
                    continue
                if a[0] == 'Average':
                    self.averageCell = np.zeros((3, 3))
                    self.averageCellRms = np.zeros((3, 3))
                    for i in range(3):
                        a = [float(j) for j in f.readline().strip().split()]
                        self.averageCell[i, :] = np.array(a[0:3])
                        self.averageCellRms[i, :] = np.array(a[3:6])
                    continue


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        OUTPUT = Output(sys.argv[1])
    else:
        OUTPUT = Output("OUTPUT")
