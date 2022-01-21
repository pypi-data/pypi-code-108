import datetime as DT
import warnings, os


class base:
    def __init__(self, workingDirectory, testName, **kwargs):
        # required to run
        # self.pathPrefix = pathPrefix  # NOLONGER used to write/read all simulation files (see workingDirectory)
        self.workingDirectory = workingDirectory
        self.testName = testName
        self.fNameBase = testName  # fNameBase                                 # used to write filename base (as available)
        self.cmtbRootDir = os.getcwd()  # grabs root directory of cmtb
        self.dateStringFmt = "%Y%m%dT%H%M%SZ"  # used as datestring format for all non
        self.namelistfile = None
        self.versionPrefix = kwargs.get('versionPrefix', 'base')

        # model specific conversions
        # WRR direction flags
        self.generateFiles = kwargs.get('generateFlag', True)
        self.runFlag = kwargs.get('runFlag', True)  # should this simulation be run?
        self.pbsFlag = kwargs.get('pbsFlag', False)  # is this running on an hpc with pbs?
        self.hpcCores = kwargs.get('hpcCores', 36)
        self.hpcNodes = kwargs.get('hpcNodes', 1)
        self.readFlag = kwargs.get('readFlag', True)  # read the simulation output
        self.rawOut = kwargs.get('rawOut', False)  # keep read input to raw files only
        self.hotStartFlag = kwargs.get('hotStartFlag', False)
        self.newModelParams = kwargs.get('newModelParams', {})  # hold dictionary for updates to
        # default parameters

        # encouraged
        self.versionPrefix = kwargs.get('versionPrefix', None)  # used to keep track of the version prefix
        self.startTime = kwargs.get('startTime', None)  # simulation start (in python datetime)
        self.endTime = kwargs.get('endTime', None)
        try:  # simulation end (in python datetime)
            self.dateString = kwargs.get('dateString',
                                         self.startTime.strftime('%Y%m%dT%H%M%SZ'))  # track the dateString
        except:
            print('No Time assigned')
        # optional, but tracked across all models to stay consistent
        self.simulationWallTime = kwargs.get('simulationWallTime', None)  # keep track of simulation wall time
        self.simulationCoreCount = kwargs.get('simulationCoreCount', None)  # keep track of how many cores were used
        # to run the simulation

        self.savePoints = kwargs.get('savePoints', None)  # keep track of where we're saving data
        self.nx = kwargs.get('nx', None)  # track number of cells in X
        self.ny = kwargs.get('ny', None)  # track number of cells in y
        self.dx = kwargs.get('dx', None)  # track resolution in x (regular grid)
        self.dy = kwargs.get('dy', None)  # track resolution in y (regular grid)
        self.nodeCount = kwargs.get('nodeCount', None)  # number of nodes in unstructured grid

        try:  # build directories if self.versionPrefix is available
            #            self.workingDirectory = kwargs.get('workingDirectory', os.path.join(self.workingDirectory,
            #                                                                    self.modelName, self.versionPrefix, self.fNameBase))
            self.workingDirectory = os.path.join(self.workingDirectory, testName)
            self.plottingDirectory = kwargs.get('plottingDirectory', os.path.join(self.workingDirectory, 'figures'))
            self.pickleSaveName = kwargs.get('pickleSaveName', os.path.join(self.workingDirectory,
                                                                            self.fNameBase + '_ww3io.pickle'))
            self.restartDirectory = kwargs.get('restartDirectory', None)

        except TypeError:
            warnings.warn('No versionPrefix: Did not create self.[workingDirectory/path structures] for wrr class')

    def write_pbs(self, model, walltime, runcode, queue='adh', allocation='ERDCV81008CMT', runname='CMTB',
                  pbsout='out.pbs', ncpus=36, mpiprocs=36):

        f = open(os.path.join(self.workingDirectory, 'submit_script.pbs'), 'w')
        f.write('#!/bin/bash\n')
        f.write('#\n')
        f.write('#PBS -N {}_{} \n'.format(model, runname))
        f.write('#PBS -q {}\n'.format(queue))
        f.write('#PBS -A {}\n'.format(allocation))
        f.write('#PBS -l select={}:ncpus={}:mpiprocs={}\n'.format(self.hpcNodes, ncpus, mpiprocs))
        f.write('#PBS -l walltime={}\n'.format(DT.datetime.strftime(walltime, '%H:%M:%S')))
        f.write('#PBS -j oe\n')
        f.write('#PBS -o {}\n'.format(pbsout))
        f.write('\n')
        f.write('cd $PBS_O_WORKDIR\n')
        for ii in runcode:
            f.write('{}\n'.format(ii))

        f.write('# ----------------------------------------------------------------\n')
        f.write('# end submit script\n')
        f.write('# -------------------------------------------------------------\n')
        f.close()
