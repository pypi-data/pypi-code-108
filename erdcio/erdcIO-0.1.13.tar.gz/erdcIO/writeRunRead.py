import numpy as np
import datetime as DT
import warnings, glob, os, shutil
import pickle as pickle
from testbedutils import sblib as sb
from testbedutils import dirtLib
import netCDF4 as nc
import f90nml
import collections
from subprocess import check_output


class base:
    def __init__(self, workingDirectory, testName, **kwargs):
        # required to run
        # self.pathPrefix = pathPrefix  # NOLONGER used to write/read all simulation files (see workingDirectory)
        self.workingDirectory = workingDirectory
        self.testName = testName
        self.fNameBase = testName #fNameBase                                 # used to write filename base (as available)
        self.cmtbRootDir = os.getcwd()                             # grabs root directory of cmtb
        self.dateStringFmt = "%Y%m%dT%H%M%SZ"                      # used as datestring format for all non
        self.namelistfile = None
        self.versionPrefix = kwargs.get('versionPrefix','base')

                                                                                          # model specific conversions
        # WRR direction flags
        self.generateFiles = kwargs.get('generateFlag', True)
        self.runFlag = kwargs.get('runFlag', True)                            # should this simulation be run?
        self.pbsFlag = kwargs.get('pbsFlag', False)                         # is this running on an hpc with pbs?
        self.hpcCores = kwargs.get('hpcCores',36)
        self.hpcNodes = kwargs.get('hpcNodes',1)
        self.readFlag = kwargs.get('readFlag', True)                     # read the simulation output
        self.rawOut = kwargs.get('rawOut', False)                             # keep read input to raw files only
        self.hotStartFlag = kwargs.get('hotStartFlag',False)
        self.newModelParams = kwargs.get('newModelParams', {})               # hold dictionary for updates to
                                                                                  # default parameters
        
        # encouraged
        self.versionPrefix = kwargs.get('versionPrefix', None)                # used to keep track of the version prefix
        self.startTime = kwargs.get('startTime', None)                        # simulation start (in python datetime)
        self.endTime = kwargs.get('endTime', None)
        try:# simulation end (in python datetime)
            self.dateString = kwargs.get('dateString', self.startTime.strftime('%Y%m%dT%H%M%SZ'))     # track the dateString
        except:
            print('No Time assigned')
        # optional, but tracked across all models to stay consistent
        self.simulationWallTime = kwargs.get('simulationWallTime', None)      # keep track of simulation wall time
        self.simulationCoreCount = kwargs.get('simulationCoreCount', None)    # keep track of how many cores were used
                                                                                # to run the simulation
        
        self.savePoints = kwargs.get('savePoints', None)                      # keep track of where we're saving data
        self.nx = kwargs.get('nx', None)                                      # track number of cells in X
        self.ny = kwargs.get('ny', None)                                      # track number of cells in y
        self.dx = kwargs.get('dx', None)                                      # track resolution in x (regular grid)
        self.dy = kwargs.get('dy', None)                                      # track resolution in y (regular grid)
        self.nodeCount = kwargs.get('nodeCount', None)                        # number of nodes in unstructured grid

        
        try:  # build directories if self.versionPrefix is available
#            self.workingDirectory = kwargs.get('workingDirectory', os.path.join(self.workingDirectory,
#                                                                    self.modelName, self.versionPrefix, self.fNameBase))
            self.workingDirectory = os.path.join(self.workingDirectory,testName)
            self.plottingDirectory = kwargs.get('plottingDirectory', os.path.join(self.workingDirectory, 'figures'))
            self.pickleSaveName = kwargs.get('pickleSaveName', os.path.join(self.workingDirectory,
                                                                            self.fNameBase+'_ww3io.pickle'))
            self.restartDirectory = kwargs.get('restartDirectory',None)
          
        except TypeError:
            warnings.warn('No versionPrefix: Did not create self.[workingDirectory/path structures] for wrr class')

    def write_pbs(self,model,walltime,runcode,queue='adh',allocation='ERDCV81008CMT',runname='CMTB',pbsout='out.pbs',ncpus=36,mpiprocs=36):
        

        f = open(os.path.join(self.workingDirectory,'submit_script.pbs'),'w')
        f.write('#!/bin/bash\n')
        f.write('#\n')
        f.write('#PBS -N {}_{} \n'.format(model,runname))
        f.write('#PBS -q {}\n'.format(queue))
        f.write('#PBS -A {}\n'.format(allocation))
        f.write('#PBS -l select={}:ncpus={}:mpiprocs={}\n'.format(self.hpcNodes,ncpus,mpiprocs))
        f.write('#PBS -l walltime={}\n'.format(DT.datetime.strftime(walltime,'%H:%M:%S')))
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

class ww3io(base):
    def __init__(self, workingDirectory, testName, **kwargs):
        """
        
        Args:
            fileNameBase:
            **kwargs:
        """
        self.modelName = 'ww3'  # model name needs to be before base init (used in base init)
        super(ww3io, self).__init__(workingDirectory,testName, **kwargs)
        # self.newModelParams = kwargs.get('newModelParams', {})
        self._replaceDefaultParams()
        f90nml.namelist.Namelist.uppercase = True
        
    def _replaceDefaultParams(self):
        """holds all default physical parameters settings for the entire model set """
        
        ## put check in place to make sure all values are used that are input into the newModelParams dictionary
        # set values with kwargs.get('string', value)
        # print list of values that are acceptable if any new model param is not used

        print('TODO: Replacing parameters.... what''s left can be warned at the end of '
              'this process [wrr._replaceDefaultParams]')
        
        # writeWW3_bouncfile
        self.ww3bounc = {'BOUND_NML':{}}
        self.ww3bounc['BOUND_NML']['BOUND%Mode'] = self.newModelParams.pop('boundaryMode', 'WRITE')
        self.ww3bounc['BOUND_NML']['BOUND%Interp'] = self.newModelParams.pop('boundaryInterp', 2)
        self.ww3bounc['BOUND_NML']['BOUND%Verbose'] = self.newModelParams.pop('boundaryVerbose', 1)
        self.ww3bounc['BOUND_NML']['BOUND%File'] = self.newModelParams.pop('boundaryfile','spec.list')

        # writeWW3_grid
        self.ww3grid = collections.OrderedDict()
        self.ww3grid['SPECTRUM_NML'] = {}
        self.ww3grid['SPECTRUM_NML']['SPECTRUM%XFR'] = self.newModelParams.pop('spectrumXFR', 1.1)         # set by def, written by input spec gen
        self.ww3grid['SPECTRUM_NML']['SPECTRUM%FREQ1'] = self.newModelParams.pop('sepctrumFREQ1', 0.038)   # set by def, written by input spec gen
        self.ww3grid['SPECTRUM_NML']['SPECTRUM%NK'] = self.newModelParams.pop('spectrumNK', 35)            # sets NKI
        self.ww3grid['SPECTRUM_NML']['SPECTRUM%NTH'] = self.newModelParams.pop('spectrumNTH', 36)
        self.ww3grid['SPECTRUM_NML']['SPECTRUM%THOFF'] = self.newModelParams.pop('spectrumTHOFF', 0)

        self.ww3grid['TIMESTEPS_NML'] = {}
        self.ww3grid['TIMESTEPS_NML']['TIMESTEPS%DTMAX'] = self.newModelParams.pop('DTMAX', 60.)
        self.ww3grid['TIMESTEPS_NML']['TIMESTEPS%DTXY'] = self.newModelParams.pop('DTXY', 60.)
        self.ww3grid['TIMESTEPS_NML']['TIMESTEPS%DTKTH'] = self.newModelParams.pop('DTKTH', 60.)
        self.ww3grid['TIMESTEPS_NML']['TIMESTEPS%DTMIN'] = self.newModelParams.pop('DTMIN', 60.)

        self.ww3grid['RUN_NML'] = {}
        self.ww3grid['RUN_NML']['RUN%FLCTH'] = self.newModelParams.pop('runFLCTH', True)
        self.ww3grid['RUN_NML']['RUN%FLCK'] = self.newModelParams.pop('runFLCK', True)
        self.ww3grid['RUN_NML']['RUN%FLSOU'] = self.newModelParams.pop('runFLSOU', True)
        self.ww3grid['RUN_NML']['RUN%FLDRY'] = self.newModelParams.pop('runDRY', False)
        self.ww3grid['RUN_NML']['RUN%FLCX'] = self.newModelParams.pop('runFLCX', True)
        self.ww3grid['RUN_NML']['RUN%FLCY'] = self.newModelParams.pop('runFLCY', True)

        self.ww3grid['GRID_NML'] = {}
        self.ww3grid['GRID_NML']['GRID%NAME'] = self.newModelParams.pop('gridNAME', self.versionPrefix)
        self.ww3grid['GRID_NML']['GRID%TYPE'] = self.newModelParams.pop('gridTYPE', 'UNST')
        self.ww3grid['GRID_NML']['GRID%COORD'] = self.newModelParams.pop('gridCOORD', 'SPHE') # or CART
        self.ww3grid['GRID_NML']['GRID%CLOS'] = self.newModelParams.pop('gridCLOSURE', 'None')
        self.ww3grid['GRID_NML']['GRID%ZLIM'] = self.newModelParams.pop('gridZLIM', 0.1)
        self.ww3grid['GRID_NML']['GRID%DMIN'] = self.newModelParams.pop('gridDMIN', 0.01)
        self.ww3grid['GRID_NML']['GRID%NML'] = self.newModelParams.pop('namelistFILENAME', 'namelists.nml')


        self.ww3grid['UNST_NML'] = {}
        self.ww3grid['UNST_NML']['UNST%SF'] = self.newModelParams.pop('unstSF', -1)
        self.ww3grid['UNST_NML']['UNST%FILENAME'] = self.newModelParams.pop('unstFILENAME', self.fNameBase + '.msh')
        self.ww3grid['UNST_NML']['UNST%IDLA'] = self.newModelParams.pop('unstIDLA', 4)
        self.ww3grid['UNST_NML']['UNST%IDFM'] = self.newModelParams.pop('unstIDFM', 1)
        self.ww3grid['UNST_NML']['UNST%FORMAT'] = self.newModelParams.pop('unstFORMAT', '(20f10.2)')

        
        # None Used in writeWW3_spec
        
        # writeWW3_shel
        #self.ww3grid = collections.OrderedDict()

        #self.IOSTYP = self.newModelParams.pop('ISOTYP', 1)
        #self.outputInterval = self.newModelParams.pop('outputInterval', 1800)  # 30 min default
        #self.outputVarString = self.newModelParams.pop('outputVarString', "HS LM T02 T01 DIR UST CHA CGE DTD FC CFX CFD")
        #self.homogeneousWinds = self.newModelParams.pop('homogeneousWinds', 'T')
        #self.homogeneousWLs = self.newModelParams.pop('homogeneousWLs', 'T')
        
        # writeWW3_ounf
        #self.fieldTimeStart = self.newModelParams.pop('fieldTimeStart', DT.datetime.strptime(os.path.basename(
        #                                        self.workingDirectory),  self.dateStringFmt).strftime('%Y%m%d %H%M%S'))
        #self.fieldTimeStride = self.newModelParams.pop('fieldTimeStride',  3600)
        
        # writeWW3_ounp
        #self.pointTimeStart = self.newModelParams.pop('pointTimeStart', DT.datetime.strptime(os.path.basename(
        #                         self.workingDirectory),  self.dateStringFmt).strftime('%Y%m%d %H%M%S'))
        #self.pointTimeStride = self.newModelParams.pop('pointTimeStride', 3600)
        for key in self.newModelParams.keys():
            warnings.warn('{} is NOT USED, please see wrr._replaceDefaultParams for help'.format(key))
        #if self.newModelParams.keys().any():
        #    raise TypeError('input params dictionary still has values in it')
        
    def _check_input(self):
        """This function checks the ensure that the proper class items are set. It is used to check before writing
         input-files (could possibly be used for output as well)"""
        # assert self.WL is not None, "Need to set your waterLevel before writing file"
        assert self.fNameBase is not None, "please write _sws first, it sets outfile name base"
        assert self.workingDirectory is not None, "must set workingDirectory "
        assert self.savePoints is not None, "save points need to be assigned"
        print('TODO: add data input checks [wrr._check_input]')
        
    def _preprocessCheck(self):
        """this function checks to make sure the path is in place and all files are in place needed to run a
        simulation. """
        print("do check to make sure all data are in place and in required input dictionaries")
        # note: this will be defined by standardized dictionaries output from prepdata
        assert os.path.exists(self.workingDirectory), "working directory isn't in place properly"
        flist = ["{}.msh".format(self.fNameBase), 'spec.list', 'ww3_grid.nml', 'ww3_ounp.nml',
                 "{}.nc".format(self.fNameBase), 'namelists.nml', 'ww3_bounc.nml', 'ww3_ounf.nml']

    def _calculateSimulationCoreCount(self):
        """Calculates core count based on grid"""
        import multiprocessing as mp
        localCoreCount = mp.cpu_count()
        self.simulationCoreCount = np.floor(self.nodeCount/500).astype(int)         # 5oo grid nodes per core
        if self.simulationCoreCount is None or self.simulationCoreCount > localCoreCount:
            self.simulationCoreCount = localCoreCount
            print("   Changed CPU count to {}".format(localCoreCount))

    def _generateRunStrings(self, modelExecutable):
    
        # preprocess string
        self.runString1 = '{}/ww3_grid > ww3_grid.out'.format(modelExecutable)
        self.runString2 = '{}/ww3_bounc > ww3_bounc.out'.format(modelExecutable)
        # run string
        tempstring = '{}/ww3_shel > ww3_shel.out'.format(modelExecutable)
        if self.pbsFlag is True:
            self.simulationCoreCount = self.hpcCores
        self.runString3 = 'mpiexec -np {}'.format(self.simulationCoreCount) + ' ' + tempstring
        # post process strings
        self.runString4 = '{}/ww3_ounf'.format(modelExecutable)
        self.runString5 = '{}/ww3_ounp'.format(modelExecutable)

    def _postprocessCheck(self):
        """This function checks to make sure all files are in the working Directory path to load."""
        spatialfname = os.path.join(self.workingDirectory, "ww3.{}.nc".format(DT.datetime.strptime(
                                                               self.dateString,   self.dateStringFmt).strftime('%Y%m')))
        pointfname = os.path.join(self.workingDirectory, "ww3.{}_spec.nc".format(DT.datetime.strptime(
            self.dateString,   self.dateStringFmt).strftime('%Y%m')))
        meshfname = os.path.join(self.workingDirectory, self.fNameBase+'.msh')
        
        for name in [pointfname, spatialfname, meshfname]:
            assert os.path.exists(name), 'missing {}'.format(name)
            
    def _processSpatialData(self, bathyDict, fieldNc):
        out = {'time': nc.date2num(nc.num2date(fieldNc['time'], fieldNc['timeUnits']), 'seconds since 1970-01-01'),
               'latitude': fieldNc['latitude'],
               'longitude': fieldNc['longitude'],
               'meshName': -999,
               'connectivity': fieldNc['tri'],
               'three': np.ones((3)) * -999,
               'nfaces': np.arange(fieldNc['tri'].shape[0], dtype=int),
               'nnodes': np.arange(bathyDict['points'].shape[0], dtype=int),
               'xFRF': np.ones_like(fieldNc['latitude']) * -999,
               'yFRF': np.ones_like(fieldNc['latitude']) * -999,
               'waveHs': fieldNc['hs'],
               'bathymetry': bathyDict['points'][:, 2],  # doesn't need to be expanded into time dimension
               'waveTm': fieldNc['t02'],
               'waveDm': fieldNc['dir'],
               'mapStatus': fieldNc['MAPSTA']
               }
        return out

    def _processStationData(self,pointNc):
        idxSorted = np.argsort(pointNc['direction'][:])
        dWEDout = pointNc['efth'][:, :, :, idxSorted]

        out = {}
        for ss, station in enumerate(nc.chartostring(pointNc['station_name'][:])):
            out[station] = {
                   'time': nc.date2num(nc.num2date(pointNc['time'][:], pointNc['timeUnits']),
                                        'seconds since 1970-01-01'),
                   'windSpeed': pointNc['wnd'][:, ss],
                   'windDirection': pointNc['wnddir'][:, ss],
                   'currentSpeed': pointNc['cur'][:, ss],
                   'currentDirection': pointNc['curdir'][:, ss],
                   'longitude': pointNc['longitude'][0, ss],  # assume static location
                   'latitude': pointNc['latitude'][0, ss],  # assume static location
                   'waveDirectionBins': pointNc['direction'][idxSorted],
                   'waveFrequency': pointNc['frequency'][:],
                   'directionalWaveEnergyDensity': dWEDout[:, ss],
                   'station_name': station
                   }
            return out

    def writeWW3_pbs(self):
        runtext = ['./ww3_grid > ww3_grid.out\n',
                   'wait\n',
                   './ww3_bounc > ww3_bounc.out\n',
                   'wait\n',
                   'mpiexec -np 36 ~/ww3_shel > ww3_shel.out\n',
                   'wait\n',
                   'mpiexec -np 1 ./ww3_ounp > ww3_ounp.out\n',
                   'wait\n',
                   './ww3_ounf > ww3_ounf.out\n']
        timing = DT.datetime(2021,1,1,6,0,0)
        self.write_pbs('ww3',timing,runtext)


    def writeWW3_bounc(self, **kwargs):
        """function will write a boundary file with prefix of self.workingDirectory+

        Args:
            **kwargs:

        Keyword Args:
            'ofname': outputfile name defaults to self.workingDirectory + 'ww3_bounc.nml'
            'specListFilename': a string or list of boundary netCDF file names (default = self.fNameBase)
            'boundaryInterp':   (default=2)  interpolation[1(nearest), 2(linear)]
            'boundaryMode':  valid ['READ', 'WRITE']  (default='WRITE')
            'boundaryVerbose':    (default=1)

        Returns:
            None

        """
        self.ww3bounc['BOUND_NML']['BOUND%File'] = kwargs.get('specListFilename', 'spec.list')
        ofname = kwargs.get('ofname', os.path.join(self.workingDirectory, 'ww3_bounc.nml'))  # required file name


        f90nml.write(self.ww3bounc,ofname,force=True)


    
    def writeWW3_speclist(self, **kwargs):
        """ writes a spectral boundary file list.

        Args:
            None

        Keyword Args:
            ofname(str): filename to write (Default os.path.join(self.workingDirectory, self.fNameBase + '.nml'))
            fileList(str/list): a list of spectral boundary files, can be a single string or list of files

        Returns:
            filename written (used in namelist)
        """
        ofname = kwargs.get('ofname', self.fNameBase + '.list')
        fileList = kwargs.get('specFiles', os.path.join(self.fNameBase + '.nc'))
        
        if not isinstance(fileList, list):
            fileList = [fileList]
        f = open(ofname, 'w+')
        for file in fileList:
            f.write('{}\n'.format(file))
        f.close()
        
        return ofname

    def create_bound(self,grid_inbindfname):
        #could come up with logic for boundaries that are continuous
        with open(grid_inbindfname, 'r') as fid:
            nodes = fid.read().splitlines()
        nodeCount = np.size(nodes)
        self.ww3grid['INBND_COUNT_NML'] = {}
        self.ww3grid['INBND_COUNT_NML']['INBND_COUNT%N_POINT'] = nodeCount
        self.ww3grid['INBND_POINT_NML'] = collections.OrderedDict()
        for ii,nn in enumerate(nodes):
            n = nn.split()
            self.ww3grid['INBND_POINT_NML']['INBND_POINT('+str(ii+1)+')'] = [int(n[0]),int(n[1]), False]

    def set_unstructured(self):
        # writeWW3_namelist
        self.ww3nml = collections.OrderedDict()
        self.ww3nml['UNST'] = collections.OrderedDict()
        self.ww3nml['UNST']['EXPFSN'] = self.newModelParams.pop('EXPFSN', False)
        self.ww3nml['UNST']['EXPFSPSI'] = self.newModelParams.pop('EXPFSPSI', False)
        self.ww3nml['UNST']['EXPFSFCT'] = self.newModelParams.pop('EXPFSFCT', False)
        self.ww3nml['UNST']['IMPFSN'] = self.newModelParams.pop('IMPFSN', False)
        self.ww3nml['UNST']['IMPTOTAL'] = self.newModelParams.pop('IMPTOTAL', True)
        self.ww3nml['UNST']['IMPREFRACTION'] = self.newModelParams.pop('IMPREFRACTION', True)
        self.ww3nml['UNST']['IMPFREQSHIFT'] = self.newModelParams.pop('IMPFREQSHIFT', True)
        self.ww3nml['UNST']['IMPSOURCE'] = self.newModelParams.pop('IMPSOURCE', True)



    def writeWW3_grid(self, grid_inbindfname=None, **kwargs):
        """Writes ww3_grid file.

        Args:
            grid_inbindfname: the offshore node description file name
            **kwargs:

        Keyword Args:
            'spectrumXFR': frequency increment (default=1.1)
            'sepctrumFREQ1': first frequency [hz] (default = 0.038)
            'spectrumNK': number of frequencies (wavenumbers)  (Default= 35)
            'spectrumNTH':  number of direction bins (default=36)
            'spectrumTHOFF': relative offset of first direction [-0.5,0.5]  (default=None)
            'runFLCTH'(bool):  direction shift  (default='T') see notes below
            'runFLCK'(bool):   wavenumber shift (default='T') see notes below
            'runFLSOU'(bool): source terms (default='T') see notes below
            'runDRY'(bool): dry run - I/O only (default='F')see notes below
            'runFLCX'(bool): x-component of propagation (default='T') see notes below
            'runFLCY'(bool): y-component of propagation (default='T') see notes below
            'DTMAX': maximum global time step (s) (default=30.)
            'DTXY': maximum CFL time step for x-y (default=30.)
            'DTKTH': maximum CFL time step for k (default=30)
            'DTMIN': minimum source term time step (default=30)
            'gridNAME': grid name (30 char) (default=self.fNameBase)
            'namelistFILENAME': namelists filename (default='namelists.nml')
            'gridTYPE': grid type (default='UNST')
            'gridCOORD': coordinate system (default='T')  see note below
            'gridCLOSURE': grid closure (default=None)
            'gridZLIM': coastline limit depth (m) (default = 0.1)
            'gridDMIN': absolute minimum water depth (default=0.01)
            'unstSF': unstructured scale factor (default=0.1)
            'unstFILENAME': unstructured filename (default=self.fNameBase+'.msh')
            'unstILDA': unstructured layout indicator (default=4)
            'unstIDFM': unstructured format indicator (default1)
            'unstFORMAT': unstructured read format (default='(20f10.2)')

            pointNumber[ii], nodeNumber[ii], ones[ii], Fs[ii]


        Notes:
            is there a way to turn True/False's as input to the required 'T' and 'F'

        Returns:

        """
        
        ofname = kwargs.get('ofname', os.path.join(self.workingDirectory, 'ww3_grid.nml')) # ww3 model assumes fname

        # alphabetical order: see self._replaceDefaultParams for setting of these values
        
        # load points for inbnd writing (boundary points)
        if grid_inbindfname is not None:
            self.create_bound(grid_inbindfname)

        f90nml.write(self.ww3grid,ofname,force=True)
    
    def writeWW3_namelist(self, **kwargs):
        """Generate the wave watch 3 namelist file.

        NOTE: is there a way to better handle T/F from booleans?

        Args:
            None: gets everything from keyword arguments and self attributes

        Keyword Args:
            'ofname'(str): name of file to write (default=os.path.join(self.workingDirectory, self.fNameBase + '.nml'))
            'UGOBCAUTO':  (default = F)
            'UGOBCDEPTH': (default = -10)
            'EXPFSN':    (default = 'F')
            'EXPFSPSI': (default = 'F')
            'EXPFSFCT':  (default = 'F')
            'IMPFSN':  (default = 'F')
            'IMPTOTAL':  (default = 'T')
            'IMPREFRACTION':  (default = 'T')
            'IMPFREQSHIFT':  (default = 'T')
            'IMPSOURCE':  (default = 'T')
            'SETUP_APPLY_WLV':  (default = 'F')
            'SOLVERTHR_SETUP': (default = 1E-14)
            'CRIT_DEP_SETUP': (default = '0.1')
            'JGS_USE_JACOBI': (default = 'T')
            'JGS_NLEVEL':  (default = 0)
            'JGS_SOURCE_NONLINEAR': (default = 'F')
            'JGS_BLOCK_GAUSS_SEIDEL':  (default = 'T')
            'JGS_TERMINATE_MAXITER':  (default = 'T')
            'JGS_MAXITER':  (default = 100000)
            'JGS_TERMINATE_NORM':  (default = 'F')
            'JGS_TERMINATE_DIFFERENCE': (default = 'T')
            'JGS_DIFF_THR': (default = 1.E-6)
            'JGS_PMIN': (default = 1.0)
            'JGS_LIMITER': (default = 'F')
            'JGS_NORM_THR': (default = 1.E-6)

        Returns:
            None

        """
        ofname = kwargs.get('ofname', os.path.join(self.workingDirectory, 'namelists.nml'))
        f90nml.write(self.ww3nml,ofname,force=True)

    def writeWW3_spec(self, data, **kwargs):
        """ write out an spectral boundary input file for WaveWatch 3 model run

        Args:
            data: dictionary with keys below:
                'wavefreqbin', 'wavedirbin', 'lon', 'lat', 'time', 'spec2d'

        Keyword Args:
            'ofname': sets filename (default is workingDirectory + fNameBase .nc)

        Returns:
            output filename (for use with bounc file)

        """
        self._check_input()
        
        ofname = kwargs.get('ofname', os.path.join(self.workingDirectory, self.fNameBase + '.nc'))
        ############ write file #########################################################
        import netCDF4 as nc
        ncfile = nc.Dataset(ofname, 'w')
        ncfile.createDimension('time', len(data['time']))
        ncfile.createDimension('station', 1)
        ncfile.createDimension('frequency', len(data['wavefreqbin']))
        ncfile.createDimension('direction', len(data['wavedirbin']))
        ncfile.createDimension('string16', 16)
        
        dataset = ncfile.createVariable('time', 'f8', ('time',))
        dataset[:] = nc.date2num(data['time'], 'days since 1990-01-01')
        setattr(dataset, 'units', 'days since 1990-01-01 00:00:00')
        setattr(dataset, 'calendar', 'gregorian')
        
        dataset = ncfile.createVariable('frequency', 'f8', ('frequency',))
        dataset[:] = data['wavefreqbin']
        dataset = ncfile.createVariable('direction', 'f8', ('direction',))
        dataset[:] = data['wavedirbin']
        dataset = ncfile.createVariable('efth', 'f8', ('time', 'station', 'frequency', 'direction',))
        # dataset[:] = efth2*180.0*np.pi
        dataset[:] = np.expand_dims(data['spec2d'], axis=1)
        
        dataset = ncfile.createVariable('station_name', 'S1', ('string16',))
        dataset[:] = nc.stringtochar(np.array(['wave            '], 'S16'))
        dataset = ncfile.createVariable('longitude', 'f4')
        dataset[:] = data['lon']
        dataset = ncfile.createVariable('latitude', 'f4')
        dataset[:] = data['lat']
        dataset = ncfile.createVariable('x', 'f4')
        dataset[:] = data['xFRF']
        dataset = ncfile.createVariable('y', 'f4')
        dataset[:] = data['yFRF']
        ncfile.close()
        
        return ofname

    def set_homogeneous(self,homog):
        homog_default = {}
        homog_default['INPUT%FORCING%WATER_LEVELS'] = False
        homog_default['INPUT%FORCING%CURRENTS'] = False
        homog_default['INPUT%FORCING%WINDS'] = False
        homog_default['INPUT%FORCING%ICE_CONC'] = False
        homog_default['INPUT%FORCING%ICE_PARAM1'] = False
        homog_default['INPUT%FORCING%ICE_PARAM2'] = False
        homog_default['INPUT%FORCING%ICE_PARAM3'] = False
        homog_default['INPUT%FORCING%ICE_PARAM4'] = False
        homog_default['INPUT%FORCING%ICE_PARAM5'] = False
        homog_default['INPUT%FORCING%MUD_DENSITY'] = False
        homog_default['INPUT%FORCING%MUD_THICKNESS'] = False
        homog_default['INPUT%FORCING%MUD_VISCOSITY'] = False
        homog_default['INPUT%ASSIM%MEAN'] = False
        homog_default['INPUT%ASSIM%SPEC1D'] = False
        homog_default['INPUT%ASSIM%SPEC2D'] = False

        homogdiff = homog == homog_default
        if not homogdiff:
            for key in homog_default:
                if (key in homog and homog_default[key] != homog[key]):
                    self.ww3shel['INPUT_NML'][key] = 'H'

    def set_homogenous_values(self,key,packet):
        startvalue = 0
        if self.hotStartFlag:
            startvalue = 1
        self.ww3shel['HOMOG_COUNT_NML']['HOMOG_COUNT%N_'+key] = len(packet['time']) - startvalue

        for ii in range(startvalue,len(packet['time'])):
            nn = ii+1+self.hhstart - startvalue
            self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT('+str(nn)+')%NAME'] = key
            self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT('+str(nn)+')%DATE'] = DT.datetime.strftime(packet['time'][ii],'%Y%m%d %H%M%S')
            if key == 'WND':
                self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT('+str(nn)+')%VALUE1'] = round(packet['avgspd'][ii],2)
                self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT('+str(nn)+')%VALUE2'] = round(packet['avgdir'][ii],1)
            elif key == 'LEV':
                self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT('+str(nn)+')%VALUE1'] = round(packet['avgWL'][ii],2)

        self.hhstart =+ len(packet['time']) - startvalue

    def writeWW3_points(self):
        """Writes points.list file from self.savePoints

        Args:
            None

        Keyword Args:
            'ofname'(str): output file name, (default=self.workingDirectory + 'points.list')

        Returns:

        """

        ofname = os.path.join(self.workingDirectory,'points.list')  # model required file name
        f = open(ofname, 'w')
        for line in self.savePoints:
            f.write("%10.5f %10.5f      %s\n" % (line[0], line[1], line[2]))
        f.close()


    def writeWW3_shel(self, startTime, endTime, windPacket=None, wlPacket=None, **kwargs):
        """Writes a ww3 shel file contains spatially constant wind and waterlevel values.

        Args:
            startTime: start time to log data (in datetime format)
            endTime: end time to log data (in datetime format)
            windPacket: a dictionary with wind data in it. has keys
                'time', 'avgVel', 'avgDir'
            WLpacket: a dictionary with water level data in it. has keys
                'time', 'avgWL'
            **kwargs: see below for valid input

        Keyword Args:
            'ofname'(str): output file name, (default=self.workingDirectory + 'ww3_shel.inp')
             'type6' (bool): output wave systems file
             'ISOTYP': how to parallelize
             'outputInterval': interval at which to output data from model (in seconds)
             'outputVarString': a string comprised of all of the data to output spatial fields of (default="HS LM T02
                    T01 DIR UST CHA CGE DTD FC CFX CFD")
             'homogeneousWinds': apply homogeneous winds, used with previous key valid values ['T', 'F'] (default = 'T')
             'homogeneousWLs': apply homogeneous WL, used with previous key valid values ['T', 'F'] (default = 'T')
             
        Returns:

        """
        ofname = os.path.join(self.workingDirectory,'ww3_shel.nml')  # model required file name

        startTime_w = startTime.strftime('%Y%m%d %H%M%S') # yyyymmdd hhmmss format.
        endTime_w = endTime.strftime('%Y%m%d %H%M%S')  # yyyymmdd hhmmss format.
        
        # set which outputs to include
        type6 = kwargs.get('type6', False)  # wave system decomposition output
        #include other output file types here

        # variables
        IOSTYP = kwargs.get('ISOTYP', 1)
        #outputInterval = self.outputInterval    # kwargs.get('outputInterval', 1800)  # 30 min default
        #outputVarString = self.outputVarString  # kwargs.get('outputVarString', "HS LM T02 T01 DIR UST CHA CGE DTD FC "
                                                #                               "CFX CFD")
        #homoWinds = self.homogeneousWinds       # kwargs.get('homogeneousWinds', 'T')
        #homoWLs = self.homogeneousWLs           # kwargs.get('homogeneousWLs', 'T')

        # things that should not change
        self.ww3shel = collections.OrderedDict()
        self.ww3shel['DOMAIN_NML'] = collections.OrderedDict()
        self.ww3shel['DOMAIN_NML']['DOMAIN%START'] = startTime_w
        self.ww3shel['DOMAIN_NML']['DOMAIN%STOP'] = endTime_w
        self.ww3shel['DOMAIN_NML']['DOMAIN%IOSTYP'] = IOSTYP

        homog = {}
        if windPacket is None:
            useWinds = False
        else:
            homog['INPUT%FORCING%WATER_LEVELS'] = True
        if wlPacket is None:
            useWLs = False
        else:
            homog['INPUT%FORCING%WINDS'] = True
        self.ww3shel['INPUT_NML'] = collections.OrderedDict()
        self.set_homogeneous(homog)

        self.ww3shel['OUTPUT_TYPE_NML'] = collections.OrderedDict()
        self.ww3shel['OUTPUT_TYPE_NML']['TYPE%FIELD%LIST'] = 'HS LM T02 T01 DIR UST CHA CGE DTD FC CFX CFD'

        self.ww3shel['OUTPUT_DATE_NML'] = collections.OrderedDict()
        self.ww3shel['OUTPUT_DATE_NML']['DATE%FIELD%START'] = startTime_w
        self.ww3shel['OUTPUT_DATE_NML']['DATE%FIELD%STRIDE'] = '1800'
        self.ww3shel['OUTPUT_DATE_NML']['DATE%FIELD%STOP'] = endTime_w
        self.ww3shel['OUTPUT_DATE_NML']['DATE%POINT%START'] = startTime_w
        self.ww3shel['OUTPUT_DATE_NML']['DATE%POINT%STRIDE'] = '1800'
        self.ww3shel['OUTPUT_DATE_NML']['DATE%POINT%STOP'] = endTime_w
        restint = endTime - startTime
        self.ww3shel['OUTPUT_DATE_NML']['DATE%RESTART'] = [startTime_w,restint.total_seconds(), endTime_w]

        self.hhstart = 0
        self.ww3shel['HOMOG_COUNT_NML'] = collections.OrderedDict()
        self.ww3shel['HOMOG_INPUT_NML'] = collections.OrderedDict()
        if 'INPUT%FORCING%WINDS' in homog:
            self.set_homogenous_values('WND',windPacket)
        if 'INPUT%FORCING%WATER_LEVELS' in homog:
            self.set_homogenous_values('LEV',wlPacket)
        if 'INPUT%FORCING%CURRENTS' in homog:
            self.set_homogenous_values('CUR',wlPpacket)

        f90nml.write(self.ww3shel,ofname,force=True)

    
    def writeWW3_ounf(self,startTime,timeStride=1800, **kwargs):
        """Write a ounf file for ww3 post processing.
        
        The ounf file contains input for post processing of WW3 field data.
        
        Keyword Args:
            startTime: start time to log data (in datetime format)
            'timeStride': Time stride for the output field (Default=1800)


        Returns:
            None
            
        """
        ofname = os.path.join(self.workingDirectory,'ww3_ounf.nml')  # model required file name

        self.ww3ounf = collections.OrderedDict()
        self.ww3ounf['FIELD_NML'] = collections.OrderedDict()
        self.ww3ounf['FIELD_NML']['FIELD%TIMESTART'] =  startTime.strftime('%Y%m%d %H%M%S')
        self.ww3ounf['FIELD_NML']['FIELD%TIMESTRIDE'] =  '{}'.format(timeStride)
        self.ww3ounf['FIELD_NML']['FIELD%LIST'] =  'HS LM T02 T01 DIR UST CHA CGE DTD FC CFX CFD'
        self.ww3ounf['FIELD_NML']['FIELD%SAMEFILE'] = True
        self.ww3ounf['FIELD_NML']['FIELD%TYPE'] =  4
        self.ww3ounf['FIELD_NML']['FIELD%TIMECOUNT'] = '1000000000'
        self.ww3ounf['FIELD_NML']['FIELD%TIMESPLIT'] = 6
        self.ww3ounf['FIELD_NML']['FIELD%PARTITION'] = '0 1 2 3'

        self.ww3ounf['FILE_NML'] = collections.OrderedDict()
        self.ww3ounf['FILE_NML']['FILE%PREFIX'] = 'ww3.'
        self.ww3ounf['FILE_NML']['FILE%NETCDF'] = 4

        f90nml.write(self.ww3ounf,ofname,force=True)
    
    def writeWW3_ounp(self,startTime,timeStride=1800, otype=1, param=1, **kwargs):
        """Write the ww3 input file for the point file post processing.
        
        The ounp file contains input for post processing of WW3 field data.
        
        Args:
            **kwargs:
        
        Keyword Args:
            startTime: start time to log data (in datetime format)
            'timeStride': Time stride for the output points (Default=1800)
        
        Returns:
            None
            
        """
        ofname = os.path.join(self.workingDirectory,'ww3_ounp.nml')  # model required file name

        self.ww3ounp = collections.OrderedDict()
        self.ww3ounp['POINT_NML'] = collections.OrderedDict()
        self.ww3ounp['POINT_NML']['POINT%TIMESTART'] = startTime.strftime('%Y%m%d %H%M%S')
        self.ww3ounp['POINT_NML']['POINT%TIMESTRIDE'] = '{}'.format(timeStride)
        self.ww3ounp['POINT_NML']['POINT%SAMEFILE'] = True
        self.ww3ounp['POINT_NML']['POINT%TYPE'] = otype
        self.ww3ounp['POINT_NML']['POINT%TIMECOUNT'] = '1000000000'
        self.ww3ounp['POINT_NML']['POINT%TIMESPLIT'] = 6
        self.ww3ounp['POINT_NML']['POINT%DIMORDER'] = True
        self.ww3ounp['POINT_NML']['POINT%LIST'] = 'all'

        self.ww3ounp['FILE_NML'] = collections.OrderedDict()
        self.ww3ounp['FILE_NML']['FILE%PREFIX'] = 'ww3.'
        self.ww3ounp['FILE_NML']['FILE%NETCDF'] = 4

        if otype == 1:
            self.ww3ounp['SPECTRA_NML'] = collections.OrderedDict()
            self.ww3ounp['SPECTRA_NML']['SPECTRA%OUTPUT'] = 3
            self.ww3ounp['SPECTRA_NML']['SPECTRA%SCALE_FAC'] = 1
            self.ww3ounp['SPECTRA_NML']['SPECTRA%OUTPUT_FAC'] = 0

        f90nml.write(self.ww3ounp,ofname,force=True)

    def writeWW3_mesh(self, **kwargs):
        """Write a ww3 mesh.  Currently passes to write_msh manual function.

        Args:
            gridNodes: a meshio grid that has objects gridNodes.points and gridNodes.cells
        
        Keyword Args:
            outFname(str): output file name (default = self.workingDirectory, self.fNameBase + '.msh')
            points (array): array of lon lat elevation values positive down (default =None)
            cell_data: dictionay containing keys ['vertex', 'triangle'] where  (default=None)
            

        Returns:

        """
        warnings.warn('This function relies on meshio, which has bad read/write for these types of grids ')
        raise NotImplementedError('try wrr.write_msh')
        # ofname = os.path.join(self.workingDirectory, self.fNameBase + '.msh')
        # mio.write_points_cells(ofname, gridNodes.points, gridNodes.cells)
        points = kwargs.get('points', None)
        cell_data = kwargs.get('cell_data', None)
        self.write_msh(points=points, cell_data=cell_data)
        self.fNameBase = 1
    
    def write_msh(self, points, cell_data, **kwargs):
        """Writes a gmsh file with associated input.
        
        Keyword Args:
            outFname(str): output file name (default = self.workingDirectory, self.fNameBase + '.msh')
            points (array): array of lon lat elevation values positive down (default =None)
            cell_data: dictionay containing keys ['vertex', 'triangle'] where  (default=None)
            version(int): version number for the gmsh type

        Returns:

        """
        gmeshVersion = kwargs.get('version', 2)
        outFname = kwargs.get('outFname', os.path.join(self.workingDirectory, self.fNameBase + '.msh'))
        self.nodeCount = cell_data['vertex'].size
        cell_dataCount = cell_data['vertex'].shape[0] + cell_data['triangle'].shape[0]
        #-------------------------------------------------------------------------------
        f = open(outFname, 'w+')
        f.write('$MeshFormat\n{} {} {}\n$EndMeshFormat\n'.format(gmeshVersion, 0, 8))
        # nodes are points, have values
        
        f.write('$Nodes\n{}\n'.format(points.shape[0]))
        for ll, line in enumerate(points):
            f.write('{0:>10}{1: >30}{2: >30}{3: >30}\n'.format(ll+1, line[0], line[1], line[2]))
        f.write('$EndNodes\n')
        
        # elements are lines between nodes
        # starts with 2 points (boundary) -- ra.cells['vertex'].shape
        # moves to 3 point (internal triangles) -- ra.cells['triangle'].shape
        # self.cell_data = {'vertex':   boundary,
        #                   'triangle': internalTriangles}
        #
        f.write('\n$Elements\n')
        f.write('{0: >14}\n'.format(cell_data['vertex'].shape[0] + cell_data['triangle'].shape[0]))
        
        for ii in range(cell_data['vertex'].shape[0]):
            f.write("        {}\n".format('      '.join(cell_data['vertex'][ii].astype(str))))
        
        for ii in range(cell_data['triangle'].shape[0]):
            f.write("        {}\n".format('      '.join(cell_data['triangle'][ii].astype(str))))
        f.write('$EndElements')
        f.close()

    def setHotStart(self,hotStartDirectory,gridName='ww3'):
       
        try:        
            rfiles = np.sort(glob.glob(os.path.join(hotStartDirectory,'restart*'+gridName)))
            shutil.copyfile(rfiles[-1],os.path.join(self.workingDirectory,'restart.'+gridName))
            print("Move restart files into working directory") 
        except:
            print("No restart file available for {}".format(gridName))

    def writeAllFiles(self, bathyPacket=None, wavePacket=None, windPacket=None, wlPacket=None, gridfname=None,
                      gridtype='unstr',updateBathy=True,hotStartDirectory=None,**kwargs):
        """Take all files from preprocess and write the model input.
        
        Args:
            wavePacket: dictionary comes from prepspec
            windPacket: dictionary comes from prepwind
            wlPacket: dictionary comes from prepWaterLevel
            bathyPacket: ictionary comes from prep_Bathy
            savepoints:
            gridfname: full/relative path for model grid

        Keyword Args:
            savePoints: these are the save points for the model run [(lon,lat,'gaugeName1'),...]
        Returns:

        """
        if self.generateFiles is True:
            self._replaceDefaultParams()  # double check we're replacing the parameters appropritely
            self._check_input()           # check to make sure all of my data are appropriately in place
            self.savePoints = kwargs.get('savePoints', self.savePoints)
            
            print('writing all {} input files '.format(self.modelName))
            specFname = self.writeWW3_spec(wavePacket)                            # write individual spec file
    
            # write grid file

            scaleFac = 1.0  # defines how to scale bathy (negative values flip positive down to positive up)
            gtemp = gridfname.rfind('.')
            self.writeWW3_grid(grid_inbindfname=gridfname[:gtemp] +'.inbnd',
                            spectrumNTH=wavePacket['spec2d'].shape[2], spectrumNK=wavePacket['spec2d'].shape[1],
                            unstSF=scaleFac)
            if os.path.exists(gridfname[:gtemp]+'.latbnd'):
                shutil.copyfile(gridfname[:gtemp]+'.latbnd',os.path.join(self.workingDirectory,'meshbnd.msh'))
            
            # write mesh file
            # ww3io.writeWW3_mesh(gridNodes=bathy)                                # write gmesh file using gmsh library
            if updateBathy is True:
                self.write_msh(points=bathyPacket.points,
                           cell_data=bathyPacket.cell_data)                       # write gmesh using manual function
            else:
                shutil.copy(gridfname,os.path.join(self.workingDirectory,self.fNameBase + '.msh'))
                self.nodeCount = bathyPacket.cell_data['vertex'].size

            # write name list file -- shouldn't change
            if gridtype == 'unstr':
                self.set_unstructured()

            # copy hotstart file if requested
            if self.hotStartFlag:
                self.setHotStart(hotStartDirectory)

            self.writeWW3_namelist()                                              # will write with defaults with no input
            
            # args
            specListFileName = self.writeWW3_speclist(ofname=os.path.join(self.workingDirectory, 'spec.list'),
                                                      specFiles=specFname.rsplit('/')[-1])       # write specFile
            
            # write files used as spectral boundary
            self.writeWW3_bounc(specListFilename=specListFileName.rsplit('/')[-1])           # write boundary files
            self.writeWW3_shel(self.startTime, self.endTime, windPacket=windPacket, wlPacket=wlPacket,               # write shel file
                               outputInterval=1800)
            self.writeWW3_points()                                                           # write the save points

            self.writeWW3_ounf(self.startTime)                                                   # process field save file
            self.writeWW3_ounp(self.startTime)                                                   # process point save file
    
            # calculate number of cores to run simulation
            self._calculateSimulationCoreCount()

    def writeWW3_pbs(self):
        runtext = ['{}\n'.format(self.runString1),'wait\n','{}\n'.format(self.runString2),'wait\n','{}\n'.format(self.runString3),'wait\n','{}\n'.format(self.runString4),'wait\n','{}\n'.format(self.runString5)]

        self.write_pbs('ww3', DT.datetime(2021, 1, 1, 3, 0, 0), runtext)
        
    def runSimulation(self, modelExecutable, hotStartDirectory=None):
        
        if self.runFlag is True:
            # generate appropriate run strings
            self._generateRunStrings(modelExecutable)
            # check appropriate data are in place
            self._preprocessCheck()
            
            # switch to directory and run
            os.chdir(self.workingDirectory)  # changing locations to where input files should be made
            print(self.workingDirectory)

            # copy hotstart file if requested
            if self.hotStartFlag:
                self.setHotStart(hotStartDirectory)

            if self.pbsFlag is True:
                self.writeWW3_pbs()
                print('PBS script has been created')
                _ = check_output("qsub submit_script.pbs", shell=True)
                print('Simultation has been submitted to the queue')
                return
            else:
                # run prepossessing scripts and simulation
                dt = DT.datetime.now()
                print('Running {} Simulation starting at {}'.format(self.modelName, dt))
                _ = check_output(self.runString1, shell=True)
                _ = check_output(self.runString2, shell=True)
                _ = check_output(self.runString3, shell=True)
                self.simulationWallTime = DT.datetime.now() - dt
                print('Simulation took {:.1f} minutes'.format(self.simulationWallTime.total_seconds()/60))
        
                # post process output data
                dt = DT.datetime.now()
                _ = check_output(self.runString4, shell=True)
                _ = check_output(self.runString5, shell=True)
                print('Simulation postProcess took {:.1f} minutes'.format((DT.datetime.now() - dt).total_seconds()/60))
                os.chdir(self.cmtbRootDir)

            # Now re-save metadata pickle, with appropriate simulation simulatedRunTime data
            with open(self.pickleSaveName, 'wb') as fid:
                pickle.dump(self, fid, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            print('I might be doing something wrong by loading and re-assigning self!!!!')
            with open(self.pickleSaveName, 'rb') as fid:
                self = pickle.load(fid)
        
    def readAllFiles(self):
        print(' TODO: readAllFiles docStrings')
        if self.readFlag is True:
            # check output
            self._postprocessCheck()
            
            fieldNC = self.readWW3_field()
            bathyDict = self.readWW3_msh()
            pointData = self.readWW3_point()
            
            # do we choose to output our data in a standard format?
            if self.rawOut is False:
                print("post process to something useful")
                spatialData = self._processSpatialData(bathyDict, fieldNC)
                stationData = self._processStationData(pointData)
                return spatialData, stationData
            else:
                return fieldNc, pointData

    def readWW3_msh(self, fname=None):
        """loads ww3 mesh, uses custom code
        
        TODO: figure out how to use meshio package

        Args:
            fname(str): a file name string

        Returns:
            # meshio object with
            writes objects to self:
                points: 3 dimensional array for each of

        """
        if fname is None:
            fname = os.path.join(self.workingDirectory, self.fNameBase+'.msh')
        f = open(fname)
        f.readline()  # '$MeshFormat\n'
        f.readline()  # '2.2 0 8\n'
        f.readline()  # '$EndMeshFormat\n'
        f.readline()  # '$Nodes\n'
        n_nodes = int(f.readline())  # '8\n'
        nodes = np.fromfile(f, count=n_nodes * 4, sep=" ").reshape((n_nodes, 4))
        n_elems = None
        while n_elems is None:
            a = f.readline()  # '$EndNodes\n'
            if a == '$Elements\n':
                n_elems = int(f.readline())
    
        boundary, internalTriangles = [], []
        for ee in range(n_elems):
            data = f.readline().split()
            if len(data) is 6:
                # if boundary will have only
                boundary.append(np.array(data, dtype=int))
            elif len(data) is 9:
                internalTriangles.append(np.array(data, dtype=int))
    
        assert f.readline().startswith('$EndElements'), "msh file didn't read properly"
        f.close()
    
        # remove bunch once
        out = {
            'points': np.array(nodes[:, 1:]),
            'cell_data': {'vertex':   np.array(boundary),
                          'triangle': np.array(internalTriangles)}}
        return out
    
        # boundary = np.array(boundary)
        # internalTriangles = np.array(internalTriangles)
        #
        # class export():
        #     def __init__(self):
        #         self.points = nodes[:, 1:]
        #         self.cell_data =
        #
        # return export
    
        # import meshio as mio
        # return mio.read(fname)  # read base grid
        #
        # except:
        #     f = open(fname, "r")
        #     ## use readlines to read all lines in the file
        #     print('Reading msh file...')
        #     # Header
        #     line = f.readline()
        #     line = f.readline()
        #     line = f.readline()
        #     line = f.readline()
        #     nvert = [int(x) for x in f.readline().split()][0]
        #
        #     # Number of elements and vertices
        #     # nelem, nvert = [int(x) for x in f.readline().split()]
        #     # print nelem
        #     # print nvert
        #
        #     indlist, lonlist, latlist, deplist= [], [], [], []
        #     for vert in range(0, nvert):
        #         dum1, dum2, dum3, dum4 = [float(x) for x in f.readline().split()]
        #         indlist.append(int(dum1))
        #         lonlist.append(float(dum2))
        #         latlist.append(float(dum3))
        #         deplist.append(float(dum4))
        #
        #     ind = np.asarray(indlist)
        #     lon = np.asarray(lonlist)
        #     lat = np.asarray(latlist)
        #     dep = np.asarray(deplist)
        #     print('... read ' + str(len(ind)) + ' vertices')
        #
        #     # print ind[len(ind)-1]
        #     # print lon[len(ind)-1]
        #     # print lat[len(ind)-1]
        #     # print dep[len(ind)-1]
        #
        #     line = f.readline()
        #     line = f.readline()
        #     nelem = int(f.readline())
        #
        #     ind2list, vert1list, vert2list, vert3list, boundnode = [], [], [], [], []
        #     for elem in range(0, nelem):
        #         dum = [int(x) for x in f.readline().split()]
        #         if dum[1] == 15:
        #             #      ind2list.append(int(dum[0]))
        #             boundnode.append(int(dum[5]))
        #         else:
        #             ind2list.append(int(dum[0]))
        #             vert1list.append(int(dum[6]))
        #             vert2list.append(int(dum[7]))
        #             vert3list.append(int(dum[8]))
        #
        #     nodeext = np.asarray(boundnode)
        #     ind2 = np.asarray(ind2list)
        #     vert1 = np.asarray(vert1list)
        #     vert2 = np.asarray(vert2list)
        #     vert3 = np.asarray(vert3list)
        #     nelem = len(ind2)
        #
        #     print('... read ' + str(len(ind2)) + ' elements')
        #     f.close()
        #
        #     # f = open(baseGridFname, "r")
        #     # ## use readlines to read all lines in the file
        #     # print('Reading msh file...')
        #     # lines = f.readlines()
        #     # f.close()
        #
        #     # # first gather node count
        #     # for ll, line in enumerate(lines):
        #     #     if line.lower() == '$nodes\n':
        #     #         nNodes = int(lines[ll+1])
        #     #         lineStart = ll
        #     #
        #     out = {'elevations': dep,
        #            'lat': lat,
        #            'lon': lon,
        #            'ind': ind,
        #            'vert1': vert1,
        #            'vert2': vert2,
        #            'vert3': vert3,
        #            'boundaries': nodeext}
        #     return out

    def readWW3_field(self, fileName=None):
        """Opens ww3 Field data and returns netCDF4 Dataset object.
        
        Notes:
            there could be a better way to do this with a different library.  For example using the xArray library or
            gridded library which is supposed to handle ugrid convetions similar to pyugrid (depricated -> gridded).

            
        Args:
            fileName(str): input file name to load (default = os.path.join(self.workingDirectory, "ww3.{}.nc".format(
                                            DT.datetime.strptime(self.dateString, self.dateStringFmt).strftime('%Y%m')))

        Returns:
            netCDF Dataset object with file using original netVar names from model run
            
        """
        if fileName is None:
            fileName = os.path.join(self.workingDirectory, "ww3.{}.nc".format(DT.datetime.strptime(self.dateString,
                                                                               self.dateStringFmt).strftime('%Y%m')))
        ncfile = nc.Dataset(fileName) #xr.load_dataset(fileName)
        ncdata = {}
        for ii in ncfile.variables:
            ncdata[ii] = ncfile[ii][:]
        ncdata['timeUnits'] = ncfile['time'].units
        return ncdata

    def readWW3_point(self, fileName=None):
        """Reads netCDF output from ww3 model and loads into netCDF4 object
        
        Args:
            fileName (str): file name for reading the ww3 point output

        Returns:
            netCDF4.Dataset object with file using original netVar names from model run


        """
        if fileName is None:
            fileName = os.path.join(self.workingDirectory, "ww3.{}_spec.nc".format(DT.datetime.strptime(self.dateString,
                                                                                self.dateStringFmt).strftime('%Y%m')))

        ncfile = nc.Dataset(fileName) #xr.load_dataset(fileName)
        ncdata = {}
        for ii in ncfile.variables:
            ncdata[ii] = ncfile[ii][:]
        ncdata['timeUnits'] = ncfile['time'].units
        return ncdata

class swashIO(base):  # actually write SWS file
    def __init__(self, fNameBase, **kwargs):
        """
        
        Args:
            fileNameBase:
            **kwargs:
        """
        self.modelName = 'swash'  # model name needs to be before base init (used in base init)
        super(swashIO, self).__init__(fNameBase, **kwargs)
        # this was removedbecause it would caue sand overwrite of input
        # self._replaceDefaultParams()
        
    def _replaceDefaultParams(self):
        """holds all default physical parameters settings for the entire model set """
        
        ## put check in place to make sure all values are used that are input into the newModelParams dictionary
        # set values with kwargs.get('string', value)
        # print list of values that are acceptable if any new model param is not used
        
        print('TODO: Replacing parameters.... what''s left can be warned at the end of '
              'this process [wrr.swashIO_replaceDefaultParams]')

        # SWS input file
        self.nLayers = self.newModelParams.pop('nLayers', 2)
        self.backVisc = self.newModelParams.pop('backVisc', 1.e-4)  # the background viscosity (in m2/s).
                                                                    # Experiences suggest a value of 10-4 to 10-3 m2/s.
        
        self.alphaBreaking = self.newModelParams.pop('alphaBreaking', 0.6)  # threshold parameter at which to initiate
                                                                                    # wave breaking
        self.betaBreaking = self.newModelParams.pop('betaBreaking', 0.3)     # threshold parameter at which to stop
                                                                                    # wave breaking.
        self.dissipationBreaking = self.newModelParams.pop('dissipationBreaking', 0.25)  # (default = 1) This value
                                                                                    # was 'used in Smits's paper 2014 CE
        self.turbModel = self.newModelParams.pop('turbModel', "KEPS")
        self.manningsN = self.newModelParams.pop('manningsN', 0.019)

        # length of sim time in [seconds]
        self.simulatedRunTime = self.newModelParams.pop('runDuration', 60*60)
        if self.simulatedRunTime > 3600:
            warnings.warn('The simulated RunTime is greater than 1 hour which could cause weird data processing '
                          'requests')

        # equilibration time in seconds for phase resolved model
        self.equlibTime = int(self.newModelParams.pop('equilbTime', 6*60))
        # convert to swash string and minutes
        self.equlibStr = self.convertTimeDeltatoSWASHString(DT.timedelta(minutes=self.equlibTime/60))

        # start recording data at time in seconds
        self.startTimeSim = self.newModelParams.pop('startTimeSim', 0.0)
        self.startTimeSimStr = self.convertTimeDeltatoSWASHString(DT.timedelta(seconds=self.startTimeSim))

        # end time calculated [s]
        self.endTimeSim = self.startTimeSim + self.simulatedRunTime + self.equlibTime
        self.endTimeSimStr = self.convertTimeDeltatoSWASHString(DT.timedelta(seconds=self.endTimeSim))

        self.sampleRate = self.newModelParams.pop('sampleRate', 0.5)           # data output sample rate [s]
        self.timestep = self.newModelParams.pop('timeStep', 0.001)             # calculation timestep [s]

        print(f"still processing {self.newModelParams.keys()} from 'modelSettings' in input file" )
        # if self.newModelParams.keys().any():
        #     raise TypeError('input params dictionary still has values in it')
        #
    def _check_input(self):
        """This function checks the ensure that the proper class items are set. It is used to check before writing
         input-files (could possibly be used for output as well)"""
        # assert self.WL is not None, "Need to set your waterLevel before writing file"
        assert self.fNameBase is not None, "please write _sws first, it sets outfile name base"
        assert self.workingDirectory is not None, "must set workingDirectory "
        assert self.equlibTime is not None, "Need to set equilibration Time before writing file"
        assert self.nLayers is not None, "Needed Value missing for writing files"

        assert self.backVisc is not None, "Needed Value missing for writing files"
        assert self.alphaBreaking is not None, "Needed Value missing for writing files"
        assert self.betaBreaking is not None, "Needed Value missing for writing files"
        assert self.dissipationBreaking is not None, "Needed Value missing for writing files"
        assert self.turbModel is not None, "Needed Value missing for writing files"
        assert self.manningsN is not None, "Needed Value missing for writing files"
 
        assert self.startTime is not None, "Needed Value missing for writing files"
        assert self.endTime is not None, "Needed Value missing for writing files"
        assert self.sampleRate is not None, "Needed Value missing for writing files"
        assert self.simulatedRunTime is not None, "Needed Value missing for writing files"
        assert self.equlibStr is not None, "Needed Value missing for writing files"
        assert self.endTimeSimStr is not None, "Needed Value missing for writing files"
        assert self.startTimeSimStr is not None, "Needed Value missing for writing files"
        assert self.timestep is not None, "Needed Value missing for writing files"

    def _preprocessCheck(self):
        """this function checks to make sure the path is in place and all files are in place needed to run a
        simulation. """
        print(" TODO: check to make sure all data are in place and in required input dictionaries ["
              "wrr.preprocessCheck]")
        # note: this will be defined by standardized dictionaries output from prepdata
        assert os.path.exists(self.workingDirectory), "working directory isn't in place properly"
        flist = ["{}.msh".format(self.fNameBase), 'spec.list', 'ww3_grid.nml', 'ww3_ounp.nml',
                 "{}.nc".format(self.fNameBase), 'namelists.nml', 'ww3_bounc.nml', 'ww3_ounf.nml']
    
    def _calculateSimulationCoreCount(self):
        """Calculates core count based on grid"""
        import multiprocessing as mp
        localCoreCount = mp.cpu_count()
        nCellPerCore = 500         # number of grid nodes per core
        self.simulationCoreCount = np.floor(self.nodeCount[0]).astype(int)
        if self.simulationCoreCount is None or self.simulationCoreCount > localCoreCount:
            self.simulationCoreCount = localCoreCount
            print("   Changed CPU count to {}".format(localCoreCount))
    
    def _generateRunStrings(self, modelExecutable):
        # preprocess string
        self.runString1 = f"mpiexec -n {self.simulationCoreCount} {modelExecutable} INPUT"
    
    def _postprocessCheck(self):
        print('Make sure all files are in the working Directory path')
    
    def _processSpatialData(self, fieldNC):
        # combine two dictionaries to one
        a = {**fieldNC[0], **fieldNC[1]}
        # round time to 1/100th of a second (resolve numerics)
        a['time'] = np.array([DT.datetime.fromtimestamp(p) for p in sb.baseRound([i.timestamp() for i in a['time']],
                                                                               0.01)])
        return a
    
    def readAllFiles(self):
        """Reads all files from Swash model.  In this model it is a single mat file.
        
        Returns:
            field data and spatial data in dictionary formats.  Since there is no save point data,
            None is returned for the save point data.

        """
        if self.readFlag is True:
            self = pickle.load(open(self.pickleSaveName, 'rb'))
            # check output
            self._postprocessCheck()
        
            fieldNC = self.loadSwash_Mat(os.path.join(self.workingDirectory, self.fNameBase+'.mat'))
        
            # do we choose to output our data in a standard format?
            if self.rawOut is False:
                spatialData = self._processSpatialData(fieldNC)
                return spatialData, None
            
            else:
                return fieldNC, None


    def writeAllFiles(self, wavePacket, windPacket, wlPacket, bathyPacket, gridfname, **kwargs):
        """Take all files from preprocess and write the model input.
        
        Args:
            wavepacket: dictionary comes from prepspec
            windpacket: dictionary comes from prepwind
            WLpacket: dictionary comes from prepWaterLevel
            bathyPacket: dictionary comes from .prep_SwashBathy
            
        Keyword Args:
            savePoints: these are the save points for the model run [(lon,lat,'gaugeName1'),...]
        Returns:

        """
        if self.generateFiles is True:
            self._replaceDefaultParams()  # double check we're replacing the parameters appropriately
            self._check_input()           # check to make sure all data is in place before write
            del windPacket, gridfname
        
            print(f'writing all {self.modelName} input files')
            self.write_sws(bathyPacket, wlPacket)
            self.write_spec1D(wavePacket['freqbins'], wavePacket['fspec'])
            self.write_bot(bathyPacket['elevation'])
            
            # calculate number of cores to run simulation
            self._calculateSimulationCoreCount()

    def runSimulation(self, modelExecutable):
        """ generates input and checks all files are in place, then runs simulation
        
        Args:
            modelExecutable: full path of model model executable
 
        Returns:
            None
            
        """
        if self.runFlag is True:
            # generate appropriate run strings
            self._generateRunStrings(modelExecutable)
            # check appropriate data are in place
            self._preprocessCheck()
        
            # switch to directory and run
            os.chdir(self.workingDirectory)  # changing locations to where input files should be made
        
            # run prepossessing scripts and simulation
            dt = DT.datetime.now()
            print('Running {} Simulation starting at {}'.format(self.modelName, dt))
            _ = check_output(self.runString1, shell=True)
            self.simulationWallTime = DT.datetime.now() - dt
            print('Simulation took {:.1f} minutes'.format(self.simulationWallTime.total_seconds()/60))
            os.chdir(self.cmtbRootDir)
        
            # Now re-save metadata pickle, with appropriate simulation simulatedRunTime data
            with open(self.pickleSaveName, 'wb') as fid:
                pickle.dump(self, fid, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            print('I might be doing something wrong by loading and re-assigning self!!!!')
            with open(self.pickleSaveName, 'rb') as fid:
                self = pickle.load(fid)

    # write functions

    def convertTimeDeltatoSWASHString(self, timeDeltaObj):
        """Function checks/converts time delta objects to swash format (in string)."""
        hours = timeDeltaObj.total_seconds() // 3600
        minutes = (timeDeltaObj.total_seconds() % 3600) // 60
        seconds = (timeDeltaObj.total_seconds() % 60)
        return "{:02}{:02}{:02}.000".format(int(hours), int(minutes), int(seconds))
    
    def write_sws(self, gridDict, WLpacket):
        """ This function writes Regular Grid input file for the SWASH model
        This function pulls Water level from the initalized class
        WRITE THIS FUNCTION FIRST

        Args:
            fNameBase(str): this function assumes all of the boundary, grid, files have the same name with
                a different file extension.  Convention is to use a datestring for the time of the model run
                (eg: YYYYmmhhTHHMMSSZ iso standard time, without ':'s )
            WLvalue (float): waterlevel value (model setup assumes NAVD88, but must be same datum as bot file)
            gridDict (dictionary): grid information
                'mx'
                'my'
                'dx'
                'dy'
                'xpc'
                'ypc'
                'alpc'

        Returns:
            None

        """
        projectName = 'VerPrefix: {}'.format(self.versionPrefix)  # meta data
        metaField2 = '_'  # meta data
        dataReturnString = 'XP YP BOTL WATL VEL VELK USTAR NHPRSK VZ'
        # note: my string notation is done with double so single quotes can be written into SWASH input file
        ##################### set variables for file write -- variable
        mx = gridDict['mx']                                    # number of bathy grid outputs
        my = gridDict['my']                                    # number of bathy grid outputs
        dx = int(gridDict['dx'])                               # mesh/grid resolution [m]
        dy = int(gridDict['dy'])                               # mesh/grid resolution [m]
        self.WL = WLpacket['avgWL'].squeeze()
        assert np.size(self.WL) == 1, "WL needs to be of value 1"
        
        ##########################
        modelStationarity = "NONSTationary"
        ModelMode = "TWODimensional"
        gridType = 'REGular'
        ##########################
        # settings  for reading grd file  -- these might change with FRF coordinate system
        ## see page 40/41 - chapter 4 of SWAN manual for  more information (SWASH and SWAN are similar)
        grdFac = 1                    # multiplication factor for all values read from file (eg 1, -1, or 0.1 for
        # decimeter conversion to [m])
        idla = 1                      # prescribes the order in which the values of bottom levels and other fields
        # should be given in file [1, 2, 3, 4 or 5]
        nhedf = 0                     # number of header lines at start of file
        nhedvec = 0                   # number of header lines in the file at the start of each component
        fortranFormat = 'FREE'        # fortran format [FREE or FORMAT]
        ###########################
        # physical parameters settings
        nLayers = self.nLayers

        backVisc = self.backVisc  # the background viscosity (in m2/s). Experiences suggest a value of 10-4 to 10-3
        alphaBreaking = self.alphaBreaking  # threshold parameter at which to initiate wave breaking
        betaBreaking = self.betaBreaking    # threshold parameter at which to stop wave breaking.
        dissipationBreaking = self.dissipationBreaking  # (default = 1) This value was used in Pieter's paper 2014 CE
        turbModel = self.turbModel
        manningsN = self.manningsN

        startTime = self.startTimeSim  # start time in seconds
        sampleRate = self.sampleRate  # sample rate in seconds
        RunTime = self.simulatedRunTime  # length of simulated time (or collection) in [seconds]
        endTime = self.endTimeSim
        equlibStr = self.equlibStr
        endTimeStr = self.endTimeSimStr
        startTimeStr = self.startTimeSimStr
        timestep = self.timestep
        
        
        ####################################
        if nLayers > 6:
            warnings.warn('Check Friction, Breaking, and Numerics, these were not previously set@@@@!!! ')
        # file names for output and read
        grdFile = '{}.grd'.format(self.fNameBase)                            # grid data
        self.ofname_sws = 'INPUT'                                                 # file we are writing out called
        botFname = '{}.bot'.format(self.fNameBase)                                # bathy elevations
        offshoreBoundaryFile = '{}.bnd'.format(self.fNameBase)               # the name of the offshore boundary
        outputMatFile = '{}.mat'.format(self.fNameBase)  # what's model output
        print(' TODO: calculate equlib time based on conditions [wrr.writeSWS]')
        ########################## set variables for file write -- static
        assert gridType in ["REGular", "CURVilinear"], "Check Grid type"  # list of grid Types available
        ##########################
        # bathymetry settings INPGRID BOTTOM
        bottomFac = -1                 # multiplaction factor for all values read from file (eg 1, -1, or 0.1 for
                                                                                        # decimeter conversion to [m])
        mxinp = int(mx-1)
        myinp = int(my-1)               # number of mesh
        dxinp = int(dx)                 # bathy grid dx
        dyinp = int(dy)                 # bathy grid dy
        xpinp = 0                       # origin in FRF coord
        ypinp = round(gridDict['ypc'])  # origin in FRF coord
        alpinp = 0                      # rotation
        ###########################
        # regular grid computational Settings
        gridType = 'REGULAR'
        # computational grid stuff
        xpc = 0                 ## set at zero for simplicity  # origin of computational grid in larger coord
        ypc = round(gridDict['ypc'])     # origin of computational grid in larger coord
        alpc = round(gridDict['alpc'])   # degrees counter clockwise rotation from true North
        xlenc = int(mxinp *dx)           # length of the computational grid in x -direction (in m).
        ylenc = int(myinp *dy)           # length of the computational grid in y -direction (in m)
        mxc = int(mxinp)                 # number of meshes in computational grid in x -direction for a uniform
        myc = int(myinp)                 # number of meshes in computational grid in y -direction for a uniform
        ### model output and compute request stuff
        outputLocationOnshore = int(ylenc/2)
        outputLocationOffshore = int(ylenc/2)
        ###################### write file now ################################################
        nowString = DT.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        f = open(os.path.join(self.workingDirectory, self.ofname_sws), 'w')
        f.write(
            "$*************HEADING***********************************\n$ Coastal Model Test Bed SWASH setup up.\n$\n$\n")
        f.write("$ file written at: {}\n".format(nowString))
        # f.write("$ wave Hs = {:.2f}; wave Tp = {:.2f}s;\n$wave Dm = {:.2f}; wave Dir Spread {}\n".format(self.Hs,
        #                                                                                                  self.Tp,
        #                                                                                                  self.Dm,
        #                                                                                                  self.spreadD))
        f.write("$ if the above are 'None', then the IO\n$ class wasn't properly initiated\n")
        f.write("PROJ '{}' '{}'\n".format(projectName[:16], metaField2))  # 16 char limit
        f.write("$\n$ This file is automatically Generated as part of CMTB\n" +
                "$ written by: Spicer Bak, with help from Julia Fieldler\n")
        f.write("$***********MODEL INPUT*********************************\n$\n")
        f.write("MODE {} {}\n".format(modelStationarity, ModelMode))
        f.write("$\n$\n$Grid Descriptors \n$\n")
        if gridType == 'REGULAR':
            #                                                [xpc] [ypc] [alpc] [xlenc] [ylenc] [mxc] [myc]
            f.write('CGRID {} {:.2f} {:.2f} {} {:6d} {:6d} {:6d} {:6d}\n'.format(gridType, xpc, ypc, alpc,
                                                                                 xlenc, ylenc, mxc, myc))
        else:
            raise NotImplementedError('Only grid currently setup is Regular')
        f.write("$\n$\n$\n$Grid coordinates file\n$\n")
        #         f.write("READinp COORdinates {} {} {} {} {} {}\n$\n".format(grdFac, grdFile,
        #         idla, nhedf, nhedvec, fortranFormat))
        #                                                [xpinp] [ypinp][alpinp][mxinp][myinp][dxinp][dyinp]
        f.write("$\nINPGRID BOTTOM {} {:.2f} {:.2f} {} {} {} {:d} {:d}\n$\n".format(gridType, xpinp, ypinp, alpinp,
                                                                                    mxinp, myinp, dxinp, dyinp))
        f.write("$\n$Vertical Layers\n$\n")
        f.write("VERT {}\n".format(nLayers))
        f.write("$\n$\n$Bathymetry values (*.bot file)\n$\n")
        f.write("READINP BOTTOM {} '{}' {} {} {}\n".format(bottomFac, botFname, idla, nhedf, fortranFormat))
        f.write("$\n$\n$Set Water Level values\n$\n")
        f.write("SET level = {}\n".format(self.WL.squeeze()))
        f.write("$\n$\n$Set Friction, Viscosity, Breaker, etc\n$\n")
        f.write("FRIC MANN {}\n".format(manningsN))
        f.write("SET BACKVISC {}\n".format(backVisc))
        f.write("BREAK {} {} {}\n".format(alphaBreaking, betaBreaking, dissipationBreaking))
        f.write("VISC VERT {}\n".format(turbModel))
        f.write("$\n$Set Spectral Boundary\n$\n")
        f.write("BOUN SIDE EAST BTYPE WEAK CON SPECfile '{}'\n".format(offshoreBoundaryFile))
        ##### NUMERICS -- HARD CODED! #####
        f.write("$\n$Set Numerics (these are hardcoded for now)\n$\n")
        f.write("$\nNONHYDROSTATIC BOX 1 PRECONDITIONER ILU\nDISCRET CORRDEP MUSCL\n")
        f.write("DISCRET UPW UMOM MOM VERT FIR\nDISCRET UPW UMOM MOM HOR MUSCL\nTIMEI 0.05 0.2\n")
        f.write("$***********MODEL OUTPUT REQUESTS*********************************\n$\n")
        f.write("GROUP 'LINE' {} {:d} {} {}\n".format(1, int(mxc), int(outputLocationOnshore), outputLocationOffshore))
        # define which output we want
        f.write("BLOCK 'LINE' NOHEAD '{}' LAY 1 {} OUTPUT  {} {} SEC\n".format(outputMatFile, dataReturnString,
                                                                               equlibStr, sampleRate))
        f.write("TEST 1 0\n")  # write out time series to print file (aka log file)
        f.write("COMPUTE {} {} SEC {}\nSTOP".format(startTimeStr, timestep, endTimeStr))
        f.close()
    
    def write_bnd(self, freqbins, dirbins, spec, loc):
        """write spectral boundary conditions, requires a preprocessing step for determining
        the df (and other things)
        Arguments:
            ofname(str): File name for output
            freqbins(array): Vector of frequency spacing of the two-dimensional spectrum
            dirbins(array): Vector of directional spacing of the two-dimensional spectrum
            spec(array): Frequency-directional spectrum (expected units is m^2/Hz/Deg). Also it
                         is assumed that the spectrum is a 2-dimensional variable with a structure
                         Spec(NFREQ,NDIR). NFREQ is the number of frequencies and NDIR is the
                         number of directions
            Loc(array): Co-ordinates for location at which boundary information is provided (i.e., Loc = [Lon,Lat])


        # this was converted from a matlab script originally for SWAN generated by:
        % Nirnimesh Kumar and George Voulgaris
        % Coastal Processes and Sediment Dynamics Lab
        % Dept. of Earth and Ocean Sciences,
        % Univ. of South Carolina, Columbia, SC
        % 03/06/2013
        % Adapted by Julia Fiedler and Nirnimesh Kumar 9/9/2014 for 1D spectrum
        % Adapted by Julia Fiedler for use in SWASH model 10/24/2016 with PUV
        % spectra
        ## adapted for python by Spicer Bak
        """
        offshoreBoundaryFile = os.path.join(self.workingDirectory, self.fNameBase + '.bnd')
        
        NLOC = 1  # Number of locations
        NFREQ = len(freqbins)  # Number of frequencies
        NDIR = len(dirbins)  # Number of directions
        rho = 1025  # SWAN allows changing rho value, but deafult is 1025 kg/m^3
        g = 9.81  # Accn. due to gravity
        ver = 'N/A'  # SWAN version
        proj = 'CMTB'  # Project Name
        Exval = -999  # Exception value
        # write file header
        f = open(offshoreBoundaryFile, 'w');
        f.write('SWASH   1                                SWASH standard spectral file, version\n');
        f.write('   Data produced by SWASH version {} \n'.format(ver))
        f.write('$   Project: {}\n'.format(proj))
        f.write('LOCATIONS                                  locations in x-y space\n')
        f.write('{}                                  number of locations'.format(NLOC))
        for loc in loc:
            f.write('%12.6f %12.6f\n'.format(loc[0], loc[1]))
        f.write('AFREQ                                   absolute frequencies in Hz\n');
        f.write('{}'.format(NFREQ));
        f.write('                                  number of frequencies\n');
        for freq in freqbins:
            f.write('{}\n'.format(freq));
        
        f.write('NDIR                                    spectral nautical directions in degr\n');
        f.write('{}'.format(NDIR))
        f.write('                                  number of directions\n');
        for waveDir in dirbins:
            f.write('{}\n'.format(waveDir))
        f.write('QUANT\n');
        f.write('     1                                  number of quantities in table\n');
        f.write('VaDens                                  variance densities in m2/Hz/degr\n');
        f.write('m2/Hz/degr                             unit\n');
        f.write('{}                          exception value\n'.format(Exval))
        
        for q in range(NLOC):
            Edens = np.squeeze(spec[q, :, :]);  # isolate single spectra
            ID = np.max(np.max(Edens))  # spectral max
            # normalize spectra so the smallest value is 1
            if ID > (10 ** (-10)):
                FAC = (1.01 * ID * 10 ** (-4))
            else:
                FAC = 10 ** (-5)
            
            Edens = Edens / FAC  # normalize spectra so no decimals
            # [[fill]align][sign][#][0][minimumwidth][.precision][type] # pep 3101
            f.write('FACTOR\n')
            f.write("{: >13.8E}\n".format(FAC))
            for r in range(NFREQ):
                f.write('{: 6d}\n'.format(np.round(Edens[r, :])))
        f.close()
    
    def write_grd(self, xCoord, yCoord):
        """write out a SWASH grd file

        Args:
            xCoord (array): array of X coordinates of mesh points
            yCoord (array): array of Y coordinates of mesh points


        """
        fname = os.path.join(self.workingDirectory, self.fNameBase+'.bot')
        # Print the grid coordinates to the grid file
        f = open(fname, 'w')
        f.write('{:12.6f}\n'.format(xCoord))
        f.write('{:12.6f}\n'.format(yCoord))
        f.close()
    
    def write_bot(self, h):
        """write bottom elevation file

        Arguments:
            h(array): array of bottom elevations 2D

        """
        self.nodeCount = np.shape(h)
        xx, yy = np.shape(h)
        fname = os.path.join(self.workingDirectory, self.fNameBase+'.bot')
        f = open(fname, 'w');
        for idxX in range(xx):
            for idxY in range(yy):
                f.write('   {:.2f}'.format(h[idxX, idxY]))
            f.write('\n')
        f.write('\n')
        f.close()
    
    def write_spec1D(self, freqbins, energy):
        """write spectral boundary condition for 1D spectra

        Args:
            freqbins(array): frequency bins for spectra
            energy(array): associated energy at each frequency [m^2/hz]

        Returns:
            None

        """
        fname = os.path.join(self.workingDirectory, '{}.bnd'.format(self.fNameBase))
        f = open(fname, 'w')
        f.write('SPEC1D\n')
        # f.write('BOUN SIDE EAST BTYPE WEAK CON\n')  # tell the model how to read file
        for i in range(len(freqbins)):
            f.write('{:10.4E} {:10.4E}\n'.format(freqbins[i], energy[i]))
        f.close()

    # Now Read functions
    
    def loadSwash_Mat(self, fname):
        """This function will load the model output file, it will pull the input water level from the
        preinitalized instance
        # file: Filename of  matlab file as generated  by  SWASH.

        Args:
            fname (str): the input file name to load

        Returns:
            Data dictionary with keys directly associated from matfile output
                'time': UTC time stamp of simulation data (after equilib time removed)
                'elevation': bottom elevation for simulation NAVD88
                'xFRF': data['Xp'].squeeze(),
                'yFRF': data['Yp'].squeeze(),
                'eta':  surface position in NAVD88
                'Ustar': magnitude of friction velocity
                'velocityU': cross-shore surface velocity
                'velocityV': surface alongshore velocities
                'velocityUprofile': cross-shore velocity profiles    [time, yFRF, xFRF, z]
                'velocityVprofile': profile of alongshore velocities [time, yFRF, xFRF, z]
                'velocityZprofile': profile of z velocities          [time, yFRF, xFRF, z]
                'NormPresProfile': profile of normalized non hydrostatic pressure

            metaDict with below keys
                'waveDm': mean direction at boundary
                'waveHs': significant wave height at boundary
                'waveTp': wave peak period at boundary
                'WL': water level used ,
                'nLayers': number of layers in model
                'nprocess': number of compute processes
                'equlibTime': equilibration time used before writing data to file
                'simWallTime': wall time it took to run simulation
                'spreadD': directional spread at boundary
                'versionPrefix': verison prefix of simulation

        """
        from scipy import io
        
        assert fname[-3:] == 'mat', 'expected output file is a matfile'
        # assert self.WL is not None, 'Needs self.WL before loading files'
        #--------------------------------------------------------------------------
        # Check how long it takes to load data
        import time
        start = time.time()
        # if the file exists, then import and parse it
        if not os.path.exists(fname):
            raise IOError('SWASH:  no simulation output file present\n{}'.format(fname))
        
        data = io.loadmat(fname)
        dataOUT, dataTemp, runMeta = {}, {}, {}
        # initalize outDict with empty arrays
        times, nonTimeDependant = [], []
        # first load all vars and parse as time dependent array
        for dictInKey, dataValues in data.items():  ## should i sort these?
            origVarName = dictInKey.split('_')
            saveKey = ''.join(origVarName[:-2])
            # print('Looking through var {} will save as {} or {}'.format(origVarName, saveKey, dictInKey))
            try:
                timeString = origVarName[-2] + '_' + origVarName[-1]
                try:
                    d = DT.datetime.strptime(timeString, "%H%M%S_%f")
                    times.append(
                        DT.timedelta(hours=d.hour, minutes=d.minute, seconds=d.second, microseconds=d.microsecond))
                    # print('saved as time step {}'.format(timeString))
                except ValueError:  # this will be things like __header__, __global__... etc, errors out on d = ...
                    runMeta[origVarName[2]] = dataValues
                    continue
                
                ######## now write data to temp dictionary
                # save data as 1D arrays, to reshape later
                # print('Original key {} put {} values into key {}'.format(origVarName, dataValues.shape, saveKey))
                if saveKey not in dataTemp:  # then haven't parsed it before, just add it
                    dataTemp[saveKey] = [dataValues]
                else:  # just add the data !
                    dataTemp[saveKey].append(dataValues)
            
            except IndexError:  # for not time dependant variables
                # print('Original key {} put {} values into key {}'.format(origVarName, dataValues.shape, dictInKey))
                # just save them as is  (variables like Xp, because save key turns into gibberish)
                nonTimeDependant.append(dictInKey)
                dataTemp[dictInKey] = [dataValues]
                # pass
        
        ################### reshape list structure to 3 d array
        # parsed quickly to a single dictionary, now reshape to [t, y, x]
        # assume that we're always outputing eta and use this to get number of timesteps
        # turn nan's to masks for output
        # tSteps, nY, nX = np.shape(dataTemp['Watlev'])
        t = DT.datetime.now()
        for var in dataTemp.keys():
            if var not in nonTimeDependant:
                dataOUT[var] = np.ma.MaskedArray(dataTemp[var], mask=np.isnan(dataTemp[var]))
        ##############################################################################
        # now restructure dictionary with a bunch of keys to a single
        # dictionary with multi dimensional output (concatenate the layered values)
        ##############################################################################
        for var in list(dataOUT.keys()):
            # if var in meshVars: # then variables have same number as layers
            saveKey = var.translate(var.maketrans('', '', '0123456789'))
            if saveKey != var:  # then there's not associated with it
                if saveKey in dataOUT:
                    dataOUT[saveKey] = np.append(dataOUT[saveKey], np.expand_dims(dataOUT[var], axis=-1), axis=-1)
                else:
                    dataOUT[saveKey] = np.expand_dims(dataOUT[var], axis=-1)
                del dataOUT[var]
        
        d1 = DT.datetime.strptime(self.fNameBase, self.dateStringFmt)
        # wrap up into output dictionary named data
        dataDict = {'time': d1 + np.unique(times),  # convert each time step to date time from time delta object
                    'elevation': data['Botlev'].squeeze(),
                    'xFRF': data['Xp'].squeeze(),
                    'yFRF': data['Yp'].squeeze(),
                    'eta': dataOUT['Watlev'],
                    'Ustar': dataOUT['Ustar'],
                    'velocityU': dataOUT['velx'],
                    'velocityUprofile': dataOUT['velkx'],
                    'velocityV': dataOUT['vely'],
                    'velocityVprofile': dataOUT['velky'],
                    'velocityZprofile': dataOUT['w'],
                    'NormPresProfile': dataOUT['Nprsk'],}
        
        metaDict = {#'waveDm': self.Dm,
                    #'waveHs': self.Hs,
                    #'waveTp': self.Tp,
                    #'WL': self.WL,
                    'nLayers': self.nLayers,
                    'nprocess': self.simulationCoreCount,
                    'equlibTime': self.equlibTime,
                    'simWallTime': self.simulationWallTime,
                    #'spreadD': self.spreadD,
                    'versionPrefix': self.versionPrefix}
        
        print(' loading SWASH data takes: {:.2f} seconds'.format(time.time()-start))
        return dataDict, metaDict


class cshoreio(base):
     def __init__(self, workingDirectory,testName, **kwargs):
         """

         Args:
             fileNameBase:
             **kwargs:
         """
         self.modelName = 'cshore'  # model name needs to be before base init (used in base init)
         super(cshoreio, self).__init__(workingDirectory,testName, **kwargs)
         # self.newModelParams = kwargs.get('newModelParams', {})
         self._replaceDefaultParams()

         timeStep = kwargs.get('timeStep', 3600)
         try:
             self.setCSHORE_time(timeStep)
         except:
             1

     def _replaceDefaultParams(self):
         """holds all default physical parameters settings for the entire model set """

         ## put check in place to make sure all values are used that are input into the newModelParams dictionary
         # set values with kwargs.get('string', value)
         # print list of values that are acceptable if any new model param is not used

         print('TODO: Replacing parameters.... what''s left can be warned at the end of '
              'this process [wrr._replaceDefaultParams]')

         self.infile = {
                # the three lines of the header for the input text file
                'iline': self.newModelParams.pop('iline', 1),  # single line
                'iprofl': self.newModelParams.pop('iprofl', 0),  # 0 = no morph, 1 = run morph
                'isedav': self.newModelParams.pop('iseday', 0),  # 0 = unlimited sand, 1 = hard bottom
                'iperm': self.newModelParams.pop('iperm', 0),  # 0 = no permeability, 1 = permeable
                'iover': self.newModelParams.pop('iover', 1),  # 0 = no overtopping , 1 = include overtopping
                'infilt': self.newModelParams.pop('infilt', 0),  # 1 = include infiltration landward of dune crest
                'iwtran': self.newModelParams.pop('iwtran', 0),  # 0 = no standing water landward of crest, 1 = wave transmission due to overtopping
                'ipond': self.newModelParams.pop('ipond', 0),  # 0 = no ponding seaward of SWL
                'iwcint': self.newModelParams.pop('iwcint', 0),  # 0 = no W & C interaction , 1 = include W & C interaction
                'iroll': self.newModelParams.pop('iroll', 0),  # 0 = no roller, 1 = roller
                'iwind': self.newModelParams.pop('iwind', 0),  # 0 = no wind effect'
                'itide': self.newModelParams.pop('itide', 0),  # 0 = no tidal effect on currents
                'iveg': self.newModelParams.pop('iveg', 0),  # 1 = include vegitation effect
                'veg_Cd': self.newModelParams.pop('veg_Cd', 1),  # vegitation drag coeff
                'veg_n': self.newModelParams.pop('veg_n', 100),  # vegitation density (units?)
                'veg_dia': self.newModelParams.pop('veg_dia', 0.01),  # vegitation diam (units? mean or median?)
                'veg_ht': self.newModelParams.pop('veg_ht', 0.20),  # vegitation height (units? mean or median?)
                'veg_rod': self.newModelParams.pop('veg_rod', 0.1),  # vegitation erosion limit below sand for failure
                'veg_extent': self.newModelParams.pop('veg_extend', np.array([.7, 1])),  # vegitation coverage as fraction of total domain length
                'gamma': self.newModelParams.pop('gamma', 0.72),  # shallow water ratio of wave height to water depth
                'sporo': self.newModelParams.pop('sporo', 0.4),  # sediment porosity
                'd50': self.newModelParams.pop('d50', 0.15),  # d_50 in mm
                'sg': self.newModelParams.pop('sg', 2.65),  # specific gravity of the sand grains
                'effb': self.newModelParams.pop('effb', 0.002),  # suspension efficiency due to breaking eB
                'efff': self.newModelParams.pop('efff', 0.004),  # suspension efficiency due to friction ef
                'slp': self.newModelParams.pop('slp', 0.5),  # suspended load parameter
                'slpot': self.newModelParams.pop('slpot', 0.1),  # overtopping suspended load parameter
                'tanphi': self.newModelParams.pop('tanphi', 0.630),  # tangent (sediment friction angle - units?)
                'blp': self.newModelParams.pop('blp', 0.002),  # bedload parameter
                'rwh': self.newModelParams.pop('iline', 0.01),  # numerical rununp wire height
                'ilab': self.newModelParams.pop('ilab', 1)
         }
                # controls the boundary condition timing. 1 uses time average while 0 requires an extra input step and solves between input-times .
               # 'fric_fac': meta_dict['fric_fac']}  # bottom friction factor

     def _generateRunStrings(self, modelExecutable):

         # preprocess string
         self.runString = '{} > infile.out'.format(modelExecutable)

     def _resultsToDict(self):

         return {'params':self.params, 'bc':self.bc, 'hydro':self.hydro, 'sed':self.sed, 'veg':self.veg,
                 'morpho':self.morpho,'meta':self.meta}

     def setCSHORE_time(self,timeStep):
         self.timeStep = timeStep
         simDuration = self.endTime - self.startTime
         self.simDuration = simDuration.total_seconds()/3600

         self.reltime = np.arange(0,simDuration.total_seconds()+timeStep,timeStep)

     def readCSHORE_nml(self,nmlname='namelist.nml'):

         #ofname = os.path.join(self.workingDirectory, nmlname)  # model required file name

         if os.path.isfile(nmlname):
             nml = f90nml.read(nmlname)

             self.newModelParams = nml['infile'].todict()

             self._replaceDefaultParams()


     def makeCSHORE_meta(self,bathyDict,waveDict,wlDict=None,ctdDict=None,dx=1,fric_fac=0.015,version='MOBILE', **kwargs):

         startTime = kwargs.get('startTime', self.startTime)
         simDuration = kwargs.get('simDuration',self.simDuration)
         timeStep = kwargs.get('timeStep',self.timeStep)

         self.meta_dict = {'startTime': startTime, 'timerun': simDuration, 'time_step': timeStep, 'dx': dx,
                           'fric_fac': fric_fac, 'version': version, 'bathy_surv_num': bathyDict['bathy_surv_num'],
                           'bathy_surv_stime': bathyDict['bathy_surv_stime'],
                           'bathy_surv_etime': bathyDict['bathy_surv_etime'],
                           'bathy_prof_num': bathyDict['bathy_prof_num'],
                           'bathy_y_max_diff': bathyDict['bathy_y_max_diff'], 'bathy_y_sdev': bathyDict['bathy_y_sdev'],
                           'BC_FRF_X': bathyDict['BC_FRF_X'], 'BC_FRF_Y': bathyDict['BC_FRF_Y'],
                           'BC_gage': waveDict['BC_gage'], 'blank_wave_data': waveDict['blank_wave_data'],
                           'blank_wl_data': wlDict['flag']}

     def makeCSHORE_bc(self,bathyDict,waveDict,wlDict=None,ctdDict=None, **kwargs):
         reltime = kwargs.get('reltime',self.reltime)

         self.BC_dict = {'timebc_wave': reltime}
         self.BC_dict['x'] = bathyDict['x']
         self.BC_dict['zb'] = bathyDict['zb']
         self.BC_dict['fw'] = bathyDict['fw']

         self.BC_dict['Hs'] = waveDict['Hs']
         self.BC_dict['Tp'] = waveDict['Tp']
         self.BC_dict['angle'] = waveDict['angle']

         self.BC_dict['swlbc'] = wlDict['avgWL']  # gives me the avg water level at "date_list"
         self.BC_dict['Wsetup'] = np.zeros(len(self.BC_dict['timebc_wave']))

         if ctdDict == None:
             self.BC_dict['salin'] = 30  # salin in ppt
             self.BC_dict['temp'] = 15  # water temp in degrees C
         else:
             # DLY note 11/06/2018: this may break if we ever get getCTD() to work and the time stamps are NOT
             # the same as the cshore time steps!
             self.BC_dict['salin'] = ctdDict['salin']  # salin in ppt
             self.BC_dict['temp'] = ctdDict['temp']  # water temp in degrees C

     def writeCSHORE_infile(self, fname='infile'):
         """This function creates the input file for CSHORE model

         Args:
             fname: name of the CSHORE infile we are writing
             in_dict: header - header for the CHSORE inflile
             iline:  single line (I have no idea what this is)

             iprofl: toggle to run morphology (0 = no morph, 1 = morph)

             isedav:  0 = unlimited sand, 1 = hard bottom

             iperm:  0 = no permeability, 1 = permeable

             iover:  0 = no overtopping , 1 = include overtopping

             iwtran:  0 = no standing water landward of crest, 1 = wave transmission due to overtopping

             ipond:  0 = no ponding seaward of SWL

             infilt:  1 = include infiltration landward of dune crest

             iwcint: 0 = no W & C interaction , 1 = include W & C interaction

             iroll: - 0 = no roller, 1 = roller

             iwind: - 0 = no wind effect'

             itide: - 0 = no tidal effect on currents

             iveg: - 1 = include vegitation effect (I'm assuming)

             iclay: - this parameter is NOT specified in Brad's run_model, so the code will break if it gets here

             dxc: - profile node spacing constant dx

             gamma: - shallow water ratio of wave height to water depth (wave breaking parameter?)

             d50: - d_50 in mm

             wf: - fall velocity of sand grain

             sg: - specific gravity of the sand grains

             effb: - suspension efficiency due to breaking eB (what is this?)

             efff: - suspension efficiency due to friction ef (what is this?)

             slp: - suspended load parameter (what is this?)

             slpot: - overtopping suspended load parameter (what is this?)

             tanphi: - tangent (sediment friction angle - units?)

             blp: - bedload parameter (what is this?)

             rwh: - numerical rununp wire height (what is this? units?)

             ilab: - controls the boundary condition timing. Don't change.  BRAD SAID TO CHANGE THIS TO 1!!!!!!

             nwave: - number of wave time-steps

             nsurge: - this ostensibly is the number of water level time steps, but is always set equal to nwave...

             timebc_wave: - time-steps of the model in seconds elapsed since model start

             Tp: - spectral peak period of the waves at each BC time-step

             Hs: - WE ARE USING Hmo NOT Hrms!!!! wave height in m              ------------------- @David

             Wsetup: - wave setup in m (hard coded to be 0 at all BC time-steps)

             swlbc: - still? water level at the boundary (in m?)

             angle: - peak wave angle on the wave energy spectra at each time step (degrees?)

             NBINP: - number of bathy profile nodes

             NPINP: - I think this is for if we are running with permeable bottom?  Brad doesn't specify this in his run_model script, so it will crash if it gets to here...

             x: - x-positions of each node (0 at boundary + as move onshore in FRF coord Units - m?)

             zb: - (initial?) bed elevation of each node in survey units (m?)

             fw: - bed friction at every node (what friction model is this?!?!? ask Brad??!?!)

             x_p: - x for permeable bottom?  Brad doesn't specify this in his run_model script, so it will crash if it gets to here...

             zb_p: - elevation for permeable bottom? Brad doesn't specify this in his run_model script, so it will crash if it gets to here...

             veg_Cd: - vegetation drag coefficient (what model for drag)

             veg_n: - vegetation density (units?!?!?!?!)

             veg_dia: - vegetation dia. (units ??!?!?!?!?)

             veg_ht: - vegetation height (units?!?!?!?!)

             veg_rod: - vegitation erosion limit below sand for failure (what is this?!?!?)

         BC_dict: key angle: - boundary condition wave angle at each time-step
             timebc_wave: - boundary condition time in seconds from simulation start time

             temp: - boundary condition temperature at each time-step

             fw: -bed friction coefficient at each position

             Hs: - boundary condition wave height at each time-step

             zb: - bottom elevation at each position

             salin: -boundary condition salinity at each time-step

             Wsetup: - i think we dont actually use this one?  so this is just an array of all zeros

             Tp: - boundary condition period at each time-step

             swlbc: - average water level at the boundary at each time-step

             x: - cross-shore position of each model node.

         meta_dict: key bathy_survey_num: - survey number that the initial bathymetry was taken from
             bathy_prof_num: - profileLine number that makes up the initial cshore bathy

             blank_wave_data: - which wave data were interpolated to generate the input file

             BC_gage: - name of the wave gage used as the BC for this cshore run

             fric_fac: - this is the friction factor that is set automatically in the infile generation script

             BC_FRF_Y: - this is the yFRF location of the BC wave gage.

             BC_FRF_X: - this is the cFRF location of the BC wave gage.  I think this is rounded down to the nearest 1 m

             startTime: - start time for this particular cshore model run

             bathy_surv_stime: - this is the start time of the bathymetry survey that was used in the model

             bathy_y_sdev: - this is the standard deviation of the actualy yFRF positions of each point in the survey used in the model

             version: - MOBILE, MOBILE_RESET or FIXED right now

             timerun: - duration that each individual simulation was run.  24 hours unless specified otherwise

             dx: - grid spacing in the model. default is 1 m unless specified otherwise

             time_step: - model time-step.  1 hour unless specified otherwise


         Returns:
             will write the CSHORE infile (infile.txt) that is used as the model input.
                    will save meta data into a pickle for post processing

         """

         ofname = os.path.join(self.workingDirectory, fname)  # model required file name

          # version toggle stuff
         if self.meta_dict['version'] == 'FIXED':
             morph = 0
         elif self.meta_dict['version'] == 'MOBILE':
             morph = 1
             self.infile['iprofl'] = 1
         elif self.meta_dict['version'] == 'MOBILE_RESET':
             morph = 1
             self.infile['iprofl'] = 1
         else:
             raise NotImplementedError('Must have version that stipulates morphology on or off')

         self.infile['header'] =  ['------------------------------------------------------------',
                   'Model Time Start : %s  Profile Number:  %s' % (
                       self.meta_dict['startTime'], self.meta_dict['bathy_prof_num']),
                   '------------------------------------------------------------'],
         self.infile['dx'] = self.meta_dict['dx']
         self.infile['fric_fac'] = self.meta_dict['fric_fac']
         self.infile['wf'] = dirtLib.vfall(self.infile['d50'], self.BC_dict['temp'], self.BC_dict['salin'],
                                      self.infile['sg'])  # fall velocity of sand grain
         self.infile['timebc_wave'] = self.BC_dict['timebc_wave']
         self.infile['timebc_surg'] = self.infile['timebc_wave']  # what is this?  Why is it a separate variable?
         self.infile['nwave'] = len(
         self.infile['timebc_wave'])  # what is this? this is just the number of time steps I have?!?!?
         self.infile['nsurg'] = self.infile['nwave']  # what is this?  Why is it a separate variable

          # begin Writing file   ################################################################3
         fid = open(ofname, 'w')
         fid.write('%i \n' % len(self.infile['header']))
         for ii in range(0, len(self.infile['header'])):
             fid.write('%s \n' % self.infile['header'][ii])
         fid.write('%-8i                                  ->ILINE\n' % self.infile['iline'])
         fid.write('%-8i                                  ->IPROFL\n' % self.infile['iprofl'])
         if self.infile['iprofl'] == 1:
             fid.write('%-8i                                  ->ISEDAV\n' % self.infile['isedav'])
         fid.write('%-8i                                  ->IPERM\n' % self.infile['iperm'])
         fid.write('%-8i                                  ->IOVER\n' % self.infile['iover'])
         if self.infile['iover']:
             fid.write('%-8i                                  ->IWTRAN\n' % self.infile['iwtran'])
             if self.infile['iwtran'] == 0:
                 fid.write('%-8i                                  ->IPOND\n' % self.infile['ipond'])
         if self.infile['iover'] == 1 and self.infile['iperm'] == 0 and self.infile['iprofl'] == 1:
             fid.write('%-8i                                  ->INFILT\n' % self.infile['infilt'])
         fid.write('%-8i                                  ->IWCINT\n' % self.infile['iwcint'])
         fid.write('%-8i                                  ->IROLL \n' % self.infile['iroll'])
         fid.write('%-8i                                  ->IWIND \n' % self.infile['iwind'])
         fid.write('%-8i                                  ->ITIDE \n' % self.infile['itide'])
         fid.write('%-8i                                  ->IVEG  \n' % self.infile['iveg'])
         if self.infile['isedav'] == 1 and self.infile['iperm'] == 0 and self.infile['iveg'] == 0:
             fid.write('%-8i                                  ->ICLAY  \n' % self.infile[
                'iclay'])  # this parameter is not specified in Brad's run_model...  This will crash if these conditions are met
         fid.write('%11.4f                                ->DXC\n' % self.infile['dx'])
         fid.write('%11.4f                                ->GAMMA \n' % self.infile['gamma'])
         if self.infile['iprofl'] == 1:
             fid.write('%11.4f%11.4f%11.4f         ->D50 WF SG\n' % (self.infile['d50'], self.infile['wf'], self.infile['sg']))
             fid.write('%11.4f%11.4f%11.4f%11.4f              ->EFFB EFFF SLP\n' % (
             self.infile['effb'], self.infile['efff'], self.infile['slp'], self.infile['slpot']))
             fid.write('%11.4f%11.4f                    ->TANPHI BLP\n' % (self.infile['tanphi'], self.infile['blp']))
         if self.infile['iover']:
             fid.write('%11.4f                               ->RWH \n' % self.infile['rwh'])
         fid.write('%-8i                                  ->ILAB\n' % self.infile['ilab'])
         if self.infile['ilab'] == 1:
             fid.write('%-8i                                  ->NWAVE \n' % self.infile['nwave'])
             fid.write('%-8i                                  ->NSURGE \n' % self.infile['nsurg'])
             for ii in range(0, len(self.BC_dict['Hs'])):
                 fid.write('%11.2f%11.4f%11.4f%11.4f%11.4f%11.4f\n' % (
                 self.BC_dict['timebc_wave'][ii], self.BC_dict['Tp'][ii], (np.sqrt(2) / 2.0) * self.BC_dict['Hs'][ii],
                 self.BC_dict['Wsetup'][ii], self.BC_dict['swlbc'][ii], self.BC_dict['angle'][ii]))
         else:
             fid.write('%-8i                                  ->NWAVE \n' % int(self.infile['nwave'] - 1))
             fid.write('%-8i                                  ->NSURGE \n' % int(self.infile['nsurg'] - 1))
             for ii in range(0, len(self.BC_dict['Hs'])):
                 fid.write('%11.2f%11.4f%11.4f%11.4f\n' % (
                 self.BC_dict['timebc_wave'][ii], self.BC_dict['Tp'][ii], (np.sqrt(2) / 2.0) * self.BC_dict['Hs'][ii],
                 self.BC_dict['angle'][ii]))
             for ii in range(0, len(self.BC_dict['swlbc'])):
                 fid.write('%11.2f%11.4f\n' % (self.infile['timebc_surg'][ii], self.BC_dict['swlbc'][ii]))

         fid.write('%-8i                             ->NBINP \n' % len(self.BC_dict['x']))

         if self.infile['iperm'] == 1 or self.infile['isedav'] >= 1:
             fid.write('%-8i                             ->NPINP \n' % len(self.BC_dict[
                                                                              'x_p']))  # this parameter is not specified in Brad's run_model...  This will crash if these conditions are met
         for ii in range(0, len(self.BC_dict['x'])):
             fid.write('%11.4f%11.4f%11.4f\n' % (self.BC_dict['x'][ii], self.BC_dict['zb'][ii], self.BC_dict['fw'][ii]))
         if self.infile['iperm'] == 1 or self.infile['isedav'] >= 1:
             for ii in range(0, len(self.BC_dict['x_p'])):
                 fid.write('%11.4f%11.4f\n' % (self.BC_dict['x_p'][ii], self.BC_dict['zb_p'][
                    ii]))  # this parameter is not specified in Brad's run_model...  This will crash if these conditions are met
         if self.infile['iveg'] == 1:
             fid.write('%5.3f                                ->VEGCD\n' % self.infile['veg_Cd'])
             for ii in range(0, len(self.BC_dict['x'])):
                 if self.BC_dict['x'][ii] >= np.max(self.BC_dict['x']) * self.infile['veg_extent'][0] and self.BC_dict['x'][ii] <= np.max(
                     self.BC_dict['x']) * self.infile['veg_extent'][1]:
                     fid.write('%11.3f%11.3f%11.3f%11.3f\n' % (
                     self.infile['veg_n'], self.infile['veg_dia'], self.infile['veg_ht'], self.infile['veg_rod']))
                 else:
                     fid.write('%11.3f%11.3f%11.3f%11.3f\n' % (0, 0, 0, 0))
         fid.close()

          # also save the metadata to a pickle file!
         fname = fname.split('/infile')
         with open(os.path.join(self.workingDirectory, "metadata.pickle"), "wb") as fid:
             pickle.dump(self.meta_dict, fid, protocol=pickle.HIGHEST_PROTOCOL)

     def writeCSHORE_pbs(self):
         runtext = ['{}\n'.format(self.runString)]

         self.write_pbs('cshore', DT.datetime(2021, 1, 1, 1, 0, 0), runtext)

     def writeAllFiles(self, bathyPacket=None, wavePacket=None, wlPacket=None, ctdPacket=None, windPacket=None,
                       hotStartDirectory=None, **kwargs):
        """Take all files from preprocess and write the model input.

        Args:
            wavepacket: dictionary comes from prepspec
            windpacket: dictionary comes from prepwind
            WLpacket: dictionary comes from prepWaterLevel
            bathyPacket: ictionary comes from prep_Bathy
            savepoints:
            gridfname: full/relative path for model grid

        Keyword Args:
            savePoints: these are the save points for the model run [(lon,lat,'gaugeName1'),...]
        Returns:

        """

        self.newModelParams = kwargs.get('newModelParams', {})               # hold dictionary for updates to

        if self.generateFiles is True:
            #self.readCSHORE_nml()
            self._replaceDefaultParams()  # double check we're replacing the parameters appropritely


            self.makeCSHORE_meta(bathyPacket, wavePacket, wlDict=wlPacket, ctdDict=ctdPacket,version=self.versionPrefix)

            self.makeCSHORE_bc(bathyPacket,wavePacket,wlDict=wlPacket,ctdDict=ctdPacket)

            self.writeCSHORE_infile()


     def runSimulation(self, modelExecutable=None,hotStartDirectory=None):
         if self.runFlag is True:
             # generate appropriate run strings
             self._generateRunStrings(modelExecutable)
             # check appropriate data are in place
             #self._preprocessCheck()

             # switch to directory and run
             os.chdir(self.workingDirectory)  # changing locations to where input files should be made

             # run simulation
             if self.pbsFlag is True:
                 self.writeCSHORE_pbs()
                 print('PBS script has been created')
                 _ = check_output("qsub submit_script.pbs", shell=True)
                 print('Simultation has been submitted to the queue')
                 return
             else:
                 dt = DT.datetime.now()
                 print('Running {} Simulation starting at {}'.format(self.modelName, dt))
                 _ = check_output(self.runString, shell=True)
                 self.simulationWallTime = DT.datetime.now() - dt
                 print('Simulation took {:.1f} minutes'.format(self.simulationWallTime.total_seconds() / 60))


                 os.chdir(self.cmtbRootDir)

        ## Now re-save metadata pickle, with appropriate simulation runtime data
        #with open(self.pickleSaveName, 'wb') as fid:
        #    pickle.dump(self, fid, protocol=pickle.HIGHEST_PROTOCOL)
    #else:
        #print('I might be doing something wrong by loading and re-assigning self!!!!')
        #with open(self.pickleSaveName, 'rb') as fid:
        #    self = pickle.load(fid)

     def readCSHORE_ODOC(self):
         """This function will Read the ODOC input file

         Args:
           path: where is this ODOC txt file you want me to read.

         Returns:
             relevant variables in an ODOC dictionary.
         """
         with open(self.workingDirectory + '/ODOC', 'r') as fid:
             tot = fid.readlines()
         fid.close()
         tot = np.asarray([s.strip() for s in tot])

         self.ODOC_dict = {}
         # find header
         row_ind = np.asarray(np.argwhere(['OPTION ILINE' in s for s in tot])).flatten()
         if len(row_ind) == 0:
             self.ODOC_dict['header'] = tot
             self.ODOC_dict['run_success'] = 0
         else:
             self.ODOC_dict['header'] = tot[0:row_ind[0]]

         # find IPROFL
         row_ind = np.asarray(np.argwhere(['OPTION IPROFL' in s for s in tot])).flatten()
         row = tot[row_ind[0]]
         self.ODOC_dict['iprofl'] = int(row[row.find('=') + 1:])

         # find ISEDAV
         row_ind = np.asarray(np.argwhere(['ISEDAV' in s for s in tot])).flatten()
         if len(row_ind) == 0:
             self.ODOC_dict['isedav'] = 0
         else:
             row = tot[row_ind[0]]
             self.ODOC_dict['isedav'] = int(row[row.find('=') + 1:row.find('=') + 3])

         # find IPERM
         row_ind = np.asarray(np.argwhere(['IMPERMEABLE' in s for s in tot])).flatten()
         if len(row_ind) == 0:
             self.ODOC_dict['iperm'] = True
         else:
             self.ODOC_dict['iperm'] = False

         # find NBINP
         row_ind = np.asarray(np.argwhere(['NBINP' in s for s in tot])).flatten()
         row = tot[row_ind[0]]
         self.ODOC_dict['nbinp'] = int(row[row.find('=') + 1:])

         # find GAMMA
         row_ind = np.asarray(np.argwhere(['Gamma' in s for s in tot])).flatten()
         row = tot[row_ind[0]]
         self.ODOC_dict['gamma'] = float(row[row.find('=') + 1:])

         # get longshore transport
         dum = tot[np.argwhere(['Transport Rate' in s for s in tot]).flatten()]
         ls_trans = np.zeros(len(dum)) * np.nan
         if len(dum) > 0:
             for ii in range(0, len(dum)):
                 row = dum[ii]
                 if len(row[row.find('=') + 1:].strip()) > 0:
                     ls_trans[ii] = float(row[row.find('=') + 1:])
                 else:
                     ls_trans[ii] = np.nan
             self.ODOC_dict['longshore_transport'] = ls_trans

         # get wave conditions at SB
         row_ind = np.asarray(np.argwhere(['INPUT WAVE' in s for s in tot])).flatten()
         ind_start = row_ind[0] + 4
         row_ind = np.asarray(np.argwhere(['INPUT BEACH AND STRUCTURE' in s for s in tot])).flatten()
         ind_end = row_ind[0] - 1
         wave_cond = tot[ind_start: ind_end]
         time_offshore = np.zeros(len(wave_cond)) * np.nan
         Tp_bc = np.zeros(len(wave_cond)) * np.nan
         Hs_bc = np.zeros(len(wave_cond)) * np.nan
         setup_bc = np.zeros(len(wave_cond)) * np.nan
         wl_bc = np.zeros(len(wave_cond)) * np.nan
         angle_bc = np.zeros(len(wave_cond)) * np.nan
         cnt = 0
         for line in wave_cond:
             dum = line.split()
             time_offshore[cnt] = float(dum[0])
             Tp_bc[cnt] = float(dum[1])
             Hs_bc[cnt] = np.sqrt(2) * float(dum[2])
             setup_bc[cnt] = float(dum[3])
             wl_bc[cnt] = float(dum[4])
             angle_bc[cnt] = float(dum[5])
             cnt = cnt + 1
         # THIS WILL ONLY RETURN THE FIRST AND LAST 10 BC POINTS!!!!
         self.ODOC_dict['time_offshore'] = time_offshore
         self.ODOC_dict['Tp_bc'] = Tp_bc
         self.ODOC_dict['Hs_bc'] = Hs_bc
         self.ODOC_dict['setup_bc'] = setup_bc
         self.ODOC_dict['wl_bc'] = wl_bc
         self.ODOC_dict['angle_bc'] = angle_bc

         # find runup
         dum2p = tot[np.argwhere(['2 percent runup' in s for s in tot]).flatten()]
         dummean = tot[np.argwhere(['Mean runup' in s for s in tot]).flatten()]
         runup_2_percent = np.zeros(len(dum2p)) * np.nan
         runup_mean = np.zeros(len(dum2p)) * np.nan
         if len(dum2p) > 0:
             for ii in range(0, len(dum2p)):
                 row1 = dum2p[ii]
                 row2 = dummean[ii]
                 if len(row1[row1.find('R2P=') + 4:].strip()) > 0:
                     runup_2_percent[ii] = float(row1[row1.find('R2P=') + 4:])
                     runup_mean[ii] = float(row2[row1.find('R2P=') + 4:])
                 else:
                     runup_2_percent[ii] = np.nan
                     runup_mean[ii] = np.nan
             self.ODOC_dict['runup_2_percent'] = runup_2_percent
             self.ODOC_dict['runup_mean'] = runup_mean

         # find jdry
         dum = tot[np.argwhere(['JDRY' in s for s in tot]).flatten()]
         jdry = np.zeros(len(dum)) * np.nan
         if len(dum) > 0:
             for ii in range(0, len(dum)):
                 row = dum[ii]
                 if len(row[row.find('JDRY=') + 5:].strip()) > 0:
                     jdry[ii] = float(row[row.find('JDRY=') + 5:])
                 else:
                     jdry[ii] = np.nan
             self.ODOC_dict['jdry'] = jdry

         # find SWL at sea boundary
         dum = tot[np.argwhere([' SWL=' in s for s in tot]).flatten()]
         swl = np.zeros(len(dum)) * np.nan
         if len(dum) > 0:
             for ii in range(0, len(dum)):
                 row = dum[ii]
                 if len(row[row.find(' SWL=') + 5:].strip()) > 0:
                     swl[ii] = float(row[row.find(' SWL=') + 5:])
                 else:
                     swl[ii] = np.nan
             self.ODOC_dict['swl'] = swl

         # find node number of SWL
         dum = tot[np.argwhere([' JSWL=' in s for s in tot]).flatten()]
         jswl = np.zeros(len(dum)) * np.nan
         if len(dum) > 0:
             for ii in range(0, len(dum)):
                 row = dum[ii]
                 if len(row[row.find(' JSWL=') + 6:].strip()) > 0:
                     jswl[ii] = float(row[row.find(' JSWL=') + 6:])
                 else:
                     jswl[ii] = np.nan
             self.ODOC_dict['jswl'] = jswl

         # find jr
         dum = tot[np.argwhere(['JR=' in s for s in tot]).flatten()]
         jr = np.zeros(len(dum)) * np.nan
         if len(dum) > 0:
             for ii in range(0, len(dum)):
                 row = dum[ii]
                 if len(row[row.find('JR=') + 3:].strip()) > 0:
                     jr[ii] = float(row[row.find('JR=') + 3:])
                 else:
                     jr[ii] = np.nan
             self.ODOC_dict['jr'] = jr

         # swash zone bottom slope
         row_ind = np.asarray(np.argwhere(['Swash zone bottom slope' in s for s in tot])).flatten()
         dum_slp = tot[row_ind]
         dum_x1 = tot[row_ind + 1]
         dum_x2 = tot[row_ind + 2]
         dum_z1 = tot[row_ind + 3]
         dum_z2 = tot[row_ind + 4]
         if len(dum_slp) > 0:
             slp = np.zeros(len(dum_slp)) * np.nan
             x1 = np.zeros(len(dum_x1)) * np.nan
             x2 = np.zeros(len(dum_x2)) * np.nan
             z1 = np.zeros(len(dum_z1)) * np.nan
             z2 = np.zeros(len(dum_z2)) * np.nan
             cnt = 0
             for ii in range(0, len(dum_slp)):
                 if len(dum_slp[ii][dum_slp[ii].find('=') + 1:].strip()) > 0:
                     slp[cnt] = float(dum_slp[ii][dum_slp[ii].find('=') + 1:])
                     x1[cnt] = float(dum_x1[ii][dum_slp[ii].find('=') + 1:])
                     x2[cnt] = float(dum_x2[ii][dum_slp[ii].find('=') + 1:])
                     z1[cnt] = float(dum_z1[ii][dum_slp[ii].find('=') + 1:])
                     z2[cnt] = float(dum_z2[ii][dum_slp[ii].find('=') + 1:])
                 else:
                     slp[cnt] = np.nan
                     x1[cnt] = np.nan
                     x2[cnt] = np.nan
                     z1[cnt] = np.nan
                     z2[cnt] = np.nan
                 cnt = cnt + 1
             self.ODOC_dict['slprun'] = slp
             self.ODOC_dict['x1run'] = x1
             self.ODOC_dict['x2run'] = x2
             self.ODOC_dict['z1run'] = z1
             self.ODOC_dict['z2run'] = z2

     def readCSHORE_infile(self,fname=None):
         """This function will read the CSHORE infile

         Args:
           path: path to input file

         Returns:
             relevant variables in an INFILE dictionary.
         """
         if fname:
             with open(fname,'r') as fid:
                 tot = fid.readlines()
         else:
             with open(self.workingDirectory + '/infile', 'r') as fid:
                 tot = fid.readlines()
         fid.close()
         tot = np.asarray([s.strip() for s in tot])

         vars = ['ILINE','IPROFL','IPERM','IOVER','IWTRAN','IPOND','IWCINT','IROLL',
                 'IWIND','ITIDE','IVEG','DXC','GAMMA']

         #blah = 'ISEDAV', 'INFILT',

         self.readIF_dict = {}

         for vv in vars:
             row_ind = np.asarray(np.argwhere([vv in s for s in tot])).flatten()
             row = tot[row_ind[0]]
             self.readIF_dict[vv.lower()] = float(row[0:row.find('-') - 1])



         # find effB, effF, and blp
         if self.readIF_dict['iprofl'] == 1:
             row_ind = np.asarray(np.argwhere(['D50' in s for s in tot])).flatten()
             row = tot[row_ind[0]]
             dummyVar = row[0:row.find('-') - 1].split()
             self.readIF_dict['d50'] = float(dummyVar[0])
             self.readIF_dict['wf'] = float(dummyVar[1])
             self.readIF_dict['sg'] = float(dummyVar[1])

             # EFFB and EFFF
             row_ind = np.asarray(np.argwhere(['EFFB' in s for s in tot])).flatten()
             row = tot[row_ind[0]]
             dummyVar = row[0:row.find('-') - 1].split()
             self.readIF_dict['effB'] = float(dummyVar[0])
             self.readIF_dict['effF'] = float(dummyVar[1])
             # BLP and TANPHI
             row_ind = np.asarray(np.argwhere(['BLP' in s for s in tot])).flatten()
             row = tot[row_ind[0]]
             dummyVar = row[0:row.find('-') - 1].split()
             self.readIF_dict['tanphi'] = float(dummyVar[0])
             self.readIF_dict['blp'] = float(dummyVar[1])
             # ILAB
             row_ind = np.asarray(np.argwhere(['ILAB' in s for s in tot])).flatten()
             row = tot[row_ind[0]]
             row[0:row.find('-') - 1]
             self.readIF_dict['ilab'] = float(row[0:row.find('-') - 1])

         # find vegetation extent
         if self.readIF_dict['iveg'] == 1:
             row_ind = np.asarray(np.argwhere(['VEGCD' in s for s in tot])).flatten()
             dummyVar = tot[row_ind[0] + 1:row_ind[0] + int(self.ODOC_dict['nbinp']) + 1]
             veg_n = np.zeros(len(dummyVar))
             veg_dia = np.zeros(len(dummyVar))
             veg_ht = np.zeros(len(dummyVar))
             veg_rod = np.zeros(len(dummyVar))
             cnt = 0
             for item in dummyVar:
                 row = item.split()
                 veg_n[cnt] = float(row[0])
                 veg_dia[cnt] = float(row[1])
                 veg_ht[cnt] = float(row[2])
                 veg_rod[cnt] = float(row[3])
                 cnt = cnt + 1
             self.readIF_dict['veg_n'] = veg_n
             self.readIF_dict['veg_dia'] = veg_dia
             self.readIF_dict['veg_ht'] = veg_ht
             self.readIF_dict['veg_rod'] = veg_rod

         # now we are going to read the BC stuff from the infile, because Brad's ODOC bc stuff ONLY HAS THE FIRST AND LAST 10!?!?! WTFWTFWTF
         # find NSURGE
         row_ind_1 = np.asarray(np.argwhere(['NSURGE' in s for s in tot])).flatten()
         row_ind_2 = np.asarray(np.argwhere(['NBINP' in s for s in tot])).flatten()
         rows = tot[row_ind_1[0] + 1:row_ind_2[0]]

         # here is where i have to deal with the ilab toggle
         # get me the length of all the rows
         row_len = np.array([len(s.split()) for s in rows])
         if 6 not in row_len:
             # this means ilab was set to zero
             # sort by length
             row_swlbc = rows[row_len == 2]
             row_waves = rows[row_len == 4]
             num_pts = len(row_swlbc)

             time_offshore = np.zeros(num_pts)
             Tp_bc = np.zeros(num_pts)
             Hs_bc = np.zeros(num_pts)
             setup_bc = np.zeros(
                 num_pts)  # the model must just assume this is zero, because this information IS NOT contained in the infile if ilab == 0
             wl_bc = np.zeros(num_pts)
             angle_bc = np.zeros(num_pts)

             for ii in range(0, len(row_waves)):
                 dum_swlbc = row_swlbc[ii].split()
                 wl_bc[ii] = dum_swlbc[1]
                 dum_waves = row_waves[ii].split()
                 time_offshore[ii] = dum_waves[0]
                 Tp_bc[ii] = dum_waves[1]
                 Hs_bc[ii] = str(np.sqrt(2) * float(dum_waves[2]))
                 angle_bc[ii] = dum_waves[3]

             self.readIF_dict['time_offshore'] = time_offshore
             self.readIF_dict['Tp_bc'] = Tp_bc
             self.readIF_dict['Hs_bc'] = Hs_bc
             self.readIF_dict['setup_bc'] = setup_bc
             self.readIF_dict['wl_bc'] = wl_bc
             self.readIF_dict['angle_bc'] = angle_bc
         else:
             # this means ilab was set to 1
             num_pts = len(rows)

             time_offshore = np.zeros(num_pts)
             Tp_bc = np.zeros(num_pts)
             Hs_bc = np.zeros(num_pts)
             setup_bc = np.zeros(num_pts)
             wl_bc = np.zeros(num_pts)
             angle_bc = np.zeros(num_pts)

             for ii in range(0, len(rows)):
                 dummyVar = rows[ii].split()
                 time_offshore[ii] = dummyVar[0]
                 Tp_bc[ii] = dummyVar[1]
                 Hs_bc[ii] = str(np.sqrt(2) * float(dummyVar[2]))
                 setup_bc[ii] = dummyVar[3]
                 wl_bc[ii] = dummyVar[4]
                 angle_bc[ii] = dummyVar[5]

             self.readIF_dict['time_offshore'] = time_offshore
             self.readIF_dict['Tp_bc'] = Tp_bc
             self.readIF_dict['Hs_bc'] = Hs_bc
             self.readIF_dict['setup_bc'] = setup_bc
             self.readIF_dict['wl_bc'] = wl_bc
             self.readIF_dict['angle_bc'] = angle_bc

     def readCSHORE_OBPROF(self):
         """This function will Read the OBPROF input file

         Args:
           path: path to OBPROF txt file

         Returns:
             relevant variables in an OBPROF dictionary.
         """
         with open(self.workingDirectory + '/OBPROF', 'r') as fid:
             tot = fid.readlines()
         fid.close()
         tot = np.asarray([s.strip() for s in tot])

         new_list = list(range(0, 1))
         if 'FIXED' in self.workingDirectory:
             new_list = list(range(0, 1))
         elif 'MOBILE' in self.workingDirectory:
             new_list = list(range(0, len(self.readIF_dict['time_offshore'])))
         else:
             print('You need to update read_CSHORE_OBPROF in inputOutput to accept the version you have specified!')
         print(new_list)
         self.OBPROF_dict = {}
         for ii in new_list:
             self.OBPROF_dict['morph%s' % str(ii + 1)] = {}
             row1 = tot[(self.ODOC_dict['nbinp'] + 1) * ii]

             if len(row1.split()) == 3:
                 N = int(row1.split()[1])
                 tme = float(row1.split()[2])
             elif len(row1.split()) == 2:
                 N = int(row1.split()[0])
                 tme = float(row1.split()[1])

             if self.readIF_dict['iveg'] > 1 and ii > 0 and self.ODOC_dict['isedav'] == 0:
                 dum = tot[(self.ODOC_dict['nbinp'] + 1) * ii + 1:(self.ODOC_dict['nbinp'] + 1) * ii + N + 1]
                 iveg = np.zeros(N)
                 x = np.zeros(N)
                 zb = np.zeros(N)
                 for ss in range(0, N):
                     iveg[ss] = float(dum[ss].split()[2])
                     x[ss] = float(dum[ss].split()[0])
                     zb[ss] = float(dum[ss].split()[1])
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['ivegetated'] = iveg
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['zb_p'] = []
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['x'] = x
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['zb'] = zb
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['time'] = tme
             elif self.ODOC_dict['isedav'] == 1:
                 dum = tot[(self.ODOC_dict['nbinp'] + 1) * ii + 1:(self.ODOC_dict['nbinp'] + 1) * ii + N + 1]
                 zb_p = np.zeros(N)
                 x = np.zeros(N)
                 zb = np.zeros(N)
                 for ss in range(0, N):
                     zb_p[ss] = float(dum[ss].split()[2])
                     x[ss] = float(dum[ss].split()[0])
                     zb[ss] = float(dum[ss].split()[1])
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['ivegetated'] = []
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['zb_p'] = zb_p
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['x'] = x
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['zb'] = zb
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['time'] = tme
             else:
                 dum = tot[(self.ODOC_dict['nbinp'] + 1) * ii + 1:(self.ODOC_dict['nbinp'] + 1) * ii + N + 1]
                 x = np.zeros(N)
                 zb = np.zeros(N)
                 for ss in range(0, N):
                     x[ss] = float(dum[ss].split()[0])
                     zb[ss] = float(dum[ss].split()[1])
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['ivegetated'] = []
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['zb_p'] = []
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['x'] = x
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['zb'] = zb
                 self.OBPROF_dict['morph%s' % str(ii + 1)]['time'] = tme

     def readCSHORE_OSETUP(self):
         """This function will Read the OSETUP input file

         Args:
           path: path to OSETUP txt file

         Returns:
             relevant variables in an OSETUP dictionary.

         """

         with open(self.workingDirectory + '/OSETUP', 'r') as fid:
             tot = fid.readlines()
         fid.close()
         tot = np.asarray([s.strip() for s in tot])

         self.OSETUP_dict = {}
         ind_track = 0
         for ii in range(0, len(self.readIF_dict['time_offshore'])):
             self.OSETUP_dict['hydro%s' % str(ii + 1)] = {}
             row1 = tot[ind_track]

             if float(row1.split()[0]) == 1:
                 N = int(row1.split()[1])
                 tme = float(row1.split()[-1])
             else:
                 N = int(row1.split()[0])

             dum = tot[ind_track + 1:ind_track + 1 + N + 1]
             x = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             setup = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             depth = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             sigma = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             Hs = np.zeros(self.ODOC_dict['nbinp']) * np.nan  # note: we are feeding it Hmo!!!!!!!
             for ss in range(0, N):
                 x[ss] = float(dum[ss].split()[0])
                 setup[ss] = float(dum[ss].split()[1])
                 depth[ss] = float(dum[ss].split()[2])
                 sigma[ss] = float(dum[ss].split()[3])
                 Hs[ss] = np.sqrt(8) * np.sqrt(2) * sigma[ss]

             ind_track = ind_track + N + 1

             self.OSETUP_dict['hydro%s' % str(ii + 1)]['x'] = x
             self.OSETUP_dict['hydro%s' % str(ii + 1)]['setup'] = setup
             self.OSETUP_dict['hydro%s' % str(ii + 1)]['depth'] = depth
             self.OSETUP_dict['hydro%s' % str(ii + 1)]['sigma'] = sigma
             self.OSETUP_dict['hydro%s' % str(ii + 1)]['Hs'] = Hs
             self.OSETUP_dict['hydro%s' % str(ii + 1)]['time_end'] = tme

     def readCSHORE_OXVELO(self):
         """This function will Read the OXVELO input file

         Args:
           path: path to  OXVELO txt file

         Returns:
             relevant variables in an OXVELO dictionary.
         """

         with open(self.workingDirectory + '/OXVELO', 'r') as fid:
             tot = fid.readlines()
         fid.close()
         tot = np.asarray([s.strip() for s in tot])

         self.OXVELO_dict = {}
         ind_track = 0
         for ii in range(0, len(self.readIF_dict['time_offshore'])):
             self.OXVELO_dict['hydro%s' % str(ii + 1)] = {}
             row1 = tot[ind_track]

             if float(row1.split()[0]) == 1:
                 N = int(row1.split()[1])
                 tme = float(row1.split()[-1])
             else:
                 N = int(row1.split()[0])

             dum = tot[ind_track + 1:ind_track + 1 + N + 1]
             x_xvelo = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             umean = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             ustd = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             for ss in range(0, N):
                 x_xvelo[ss] = float(dum[ss].split()[0])
                 umean[ss] = float(dum[ss].split()[1])
                 ustd[ss] = float(dum[ss].split()[2])

             ind_track = ind_track + N + 1

             self.OXVELO_dict['hydro%s' % str(ii + 1)]['x_xvelo'] = x_xvelo
             self.OXVELO_dict['hydro%s' % str(ii + 1)]['umean'] = umean
             self.OXVELO_dict['hydro%s' % str(ii + 1)]['ustd'] = ustd
             self.OXVELO_dict['hydro%s' % str(ii + 1)]['time_end'] = tme

     def readCSHORE_OYVELO(self):
         """This function will Read the OYVELO input file

         Args:
           path: path to OYVELO txt file

         Returns:
             relevant variables in an OYVELO dictionary.

         """
         # OYVELO reading function
         with open(self.workingDirectory + '/OYVELO', 'r') as fid:
             tot = fid.readlines()
         fid.close()
         tot = np.asarray([s.strip() for s in tot])

         tot_len = np.asarray([len(s.split()) for s in tot])
         header_ind = np.argwhere(tot_len != 4).flatten()  # it will have 4 things in the row if it actually has data

         self.OYVELO_dict = {}
         for ii in range(0, len(header_ind)):
             self.OYVELO_dict['hydro%s' % str(ii + 1)] = {}

             # get all the data in between the header inds!
             if ii == len(header_ind) - 1:
                 dum = tot[header_ind[ii]:]
             else:
                 dum = tot[header_ind[ii]:header_ind[ii + 1]]

             if float(dum[0].split()[0]) == 1:
                 N = int(dum[0].split()[1])
                 tme = float(dum[0].split()[-1])
             else:
                 N = int(dum[0].split()[0])

             # if the length of dum is <= 1, that means it ONLY has a header (i.e., no actual data)
             if len(dum) <= 1:

                 x_yvelo = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                 stheta = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                 vmean = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                 vstd = np.zeros(self.ODOC_dict['nbinp']) * np.nan

             else:
                 x_yvelo = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                 stheta = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                 vmean = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                 vstd = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                 for ss in range(1, N + 1):
                     x_yvelo[ss - 1] = float(dum[ss].split()[0])
                     stheta[ss - 1] = float(dum[ss].split()[1])
                     vmean[ss - 1] = float(dum[ss].split()[2])
                     vstd[ss - 1] = float(dum[ss].split()[3])

             self.OYVELO_dict['hydro%s' % str(ii + 1)]['x_yvelo'] = x_yvelo
             self.OYVELO_dict['hydro%s' % str(ii + 1)]['stheta'] = stheta
             self.OYVELO_dict['hydro%s' % str(ii + 1)]['vmean'] = vmean
             self.OYVELO_dict['hydro%s' % str(ii + 1)]['vstd'] = vstd
             self.OYVELO_dict['hydro%s' % str(ii + 1)]['time_end'] = tme

     def readCSHORE_OCROSS(self):
         """This function will Read the OCROSS input file

         Args:
           path: path to OCROSS txt file

         Returns:
             relevant variables in an OCROSS dictionary.

         """

         if self.ODOC_dict['iprofl'] == 1:
             self.OCROSS_dict = {}
             # OCROSS reading function
             with open(self.workingDirectory + '/OCROSS', 'r') as fid:
                 tot = fid.readlines()
             fid.close()
             tot = np.asarray([s.strip() for s in tot])

             tot_len = np.asarray([len(s.split()) for s in tot])
             header_ind = np.argwhere(
                 tot_len != 4).flatten()  # it will have 4 things in the row if it actually has data

             for ii in range(0, len(header_ind)):
                 self.OCROSS_dict['sed%s' % str(ii + 1)] = {}

                 # get all the data in between the header inds!
                 if ii == len(header_ind) - 1:
                     dum = tot[header_ind[ii]:]
                 else:
                     dum = tot[header_ind[ii]:header_ind[ii + 1]]

                 if float(dum[0].split()[0]) == 1:
                     N = int(dum[0].split()[1])
                     tme = float(dum[0].split()[-1])
                 else:
                     N = int(dum[0].split()[0])

                 # if the length of dum is <= 1, that means it ONLY has a header (i.e., no actual data)
                 if len(dum) <= 1:

                     x_cross = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qbx = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qsx = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qx = np.zeros(self.ODOC_dict['nbinp']) * np.nan

                 else:
                     x_cross = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qbx = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qsx = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qx = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     for ss in range(1, N + 1):
                         x_cross[ss - 1] = float(dum[ss].split()[0])
                         qbx[ss - 1] = float(dum[ss].split()[1])
                         qsx[ss - 1] = float(dum[ss].split()[2])
                         qx[ss - 1] = float(dum[ss].split()[3])

                 self.OCROSS_dict['sed%s' % str(ii + 1)]['x_cross'] = x_cross
                 self.OCROSS_dict['sed%s' % str(ii + 1)]['qbx'] = qbx
                 self.OCROSS_dict['sed%s' % str(ii + 1)]['qsx'] = qsx
                 self.OCROSS_dict['sed%s' % str(ii + 1)]['qx'] = qx
                 self.OCROSS_dict['sed%s' % str(ii + 1)]['time_end'] = tme

     def readCSHORE_OLONGS(self):
         """This function will Read the OLONGS input file

         Args:
           path: path to OLONGS txt file

         Returns:
             relevant variables in an OLONGS dictionary.

         """
         # OLONGS reading function - this is currently permanently turned off in Brad's script...
         if self.ODOC_dict['iprofl'] == 1:

             with open(self.workingDirectory + '/OLONGS', 'r') as fid:
                 tot = fid.readlines()
             fid.close()
             tot = np.asarray([s.strip() for s in tot])

             tot_len = np.asarray([len(s.split()) for s in tot])
             header_ind = np.argwhere(
                 tot_len != 4).flatten()  # it will have 4 things in the row if it actually has data

             self.OLONGS_dict = {}
             for ii in range(0, len(header_ind)):
                 self.OLONGS_dict['sed%s' % str(ii + 1)] = {}

                 # get all the data in between the header inds!
                 if ii == len(header_ind) - 1:
                     dum = tot[header_ind[ii]:]
                 else:
                     dum = tot[header_ind[ii]:header_ind[ii + 1]]

                 if float(dum[0].split()[0]) == 1:
                     N = int(dum[0].split()[1])
                     tme = float(dum[0].split()[-1])
                 else:
                     N = int(dum[0].split()[0])

                 # if the length of dum is <= 1, that means it ONLY has a header (i.e., no actual data)
                 if len(dum) <= 1:

                     x_long = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qby = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qsy = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qy = np.zeros(self.ODOC_dict['nbinp']) * np.nan

                 else:
                     x_long = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qby = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qsy = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     qy = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     for ss in range(1, N + 1):
                         x_long[ss - 1] = float(dum[ss].split()[0])
                         qby[ss - 1] = float(dum[ss].split()[1])
                         qsy[ss - 1] = float(dum[ss].split()[2])
                         qy[ss - 1] = float(dum[ss].split()[3])

                 self.OLONGS_dict['sed%s' % str(ii + 1)]['x_long'] = x_long
                 self.OLONGS_dict['sed%s' % str(ii + 1)]['qby'] = qby
                 self.OLONGS_dict['sed%s' % str(ii + 1)]['qsy'] = qsy
                 self.OLONGS_dict['sed%s' % str(ii + 1)]['qy'] = qy
                 self.OLONGS_dict['sed%s' % str(ii + 1)]['time_end'] = tme

     def readCSHORE_OBSUSL(self):
         """This function will Read the OBSUSL input file

         Args:
           path: path to OBSUSL txt file

         Returns:
             relevant variables in an OBSUSL dictionary.
         """
         # OBSUSL reading function
         if self.ODOC_dict['iprofl'] == 1:

             with open(self.workingDirectory + '/OBSUSL', 'r') as fid:
                 tot = fid.readlines()
             fid.close()
             tot = np.asarray([s.strip() for s in tot])

             tot_len = np.asarray([len(s.split()) for s in tot])
             header_ind = np.argwhere(
                 tot_len != 4).flatten()  # it will have 4 things in the row if it actually has data

             self.OBSUSL_dict = {}
             for ii in range(0, len(header_ind)):
                 self.OBSUSL_dict['sed%s' % str(ii + 1)] = {}

                 # get all the data in between the header inds!
                 if ii == len(header_ind) - 1:
                     dum = tot[header_ind[ii]:]
                 else:
                     dum = tot[header_ind[ii]:header_ind[ii + 1]]

                 if float(dum[0].split()[0]) == 1:
                     N = int(dum[0].split()[1])
                     tme = float(dum[0].split()[-1])
                 else:
                     N = int(dum[0].split()[0])

                 # if the length of dum is <= 1, that means it ONLY has a header (i.e., no actual data)
                 if len(dum) <= 1:

                     x_susl = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     ps = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     pb = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     vs = np.zeros(self.ODOC_dict['nbinp']) * np.nan

                 else:
                     x_susl = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     ps = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     pb = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     vs = np.zeros(self.ODOC_dict['nbinp']) * np.nan
                     for ss in range(1, N + 1):
                         x_susl[ss - 1] = float(dum[ss].split()[0])
                         ps[ss - 1] = float(dum[ss].split()[1])
                         pb[ss - 1] = float(dum[ss].split()[2])
                         vs[ss - 1] = float(dum[ss].split()[3])

                 self.OBSUSL_dict['sed%s' % str(ii + 1)]['x_susl'] = x_susl
                 self.OBSUSL_dict['sed%s' % str(ii + 1)]['ps'] = ps
                 self.OBSUSL_dict['sed%s' % str(ii + 1)]['pb'] = pb
                 self.OBSUSL_dict['sed%s' % str(ii + 1)]['vs'] = vs
                 self.OBSUSL_dict['sed%s' % str(ii + 1)]['time_end'] = tme

     def gatherCSHORE_params(self):

         self.params = {}
         self.params['header'] = self.ODOC_dict['header']
         self.params['iprofl'] = self.ODOC_dict['iprofl']
         self.params['isedav'] = self.ODOC_dict['isedav']
         self.params['iperm'] = self.ODOC_dict['iperm']
         self.params['nbinp'] = self.ODOC_dict['nbinp']
         self.params['gamma'] = self.ODOC_dict['gamma']
         self.params['iover'] = self.readIF_dict['iover']
         self.params['iveg'] = self.readIF_dict['iveg']
         if 'MOBILE' in self.workingDirectory:
             self.params['effB'] = self.readIF_dict['effB']
             self.params['effF'] = self.readIF_dict['effF']
             self.params['tanphi'] = self.readIF_dict['tanphi']
             self.params['blp'] = self.readIF_dict['tanphi']
             self.params['ilab'] = self.readIF_dict['ilab']
         else:
             pass

         num_steps = len(list(self.OSETUP_dict.keys()))
         self.params['num_steps'] = num_steps

     def gatherCSHORE_bc(self):
         self.bc = {}
         self.bc['time_offshore'] = self.readIF_dict['time_offshore']
         self.bc['waveTpOffshore'] = self.readIF_dict['Tp_bc']
         self.bc['waveHsOffshore'] = self.readIF_dict['Hs_bc']
         self.bc['waveSetupOffshore'] = self.readIF_dict['setup_bc']
         self.bc['waterLevelOffshore'] = self.readIF_dict['wl_bc']
         self.bc['waveMeanDirectionOffshore'] = self.readIF_dict['angle_bc']

     def gatherCSHORE_waves(self):
         self.waves = {}


     def gatherCSHORE_hydro(self):
         self.hydro = {}
         self.hydro['runup_2_percent'] = self.ODOC_dict['runup_2_percent'].reshape(
             self.ODOC_dict['runup_2_percent'].shape[0], -1)
         self.hydro['runup_mean'] = self.ODOC_dict['runup_mean'].reshape(self.ODOC_dict['runup_mean'].shape[0], -1)
         self.hydro['jdry'] = self.ODOC_dict['jdry'].reshape(self.ODOC_dict['jdry'].shape[0], -1)
         self.hydro['swl'] = self.ODOC_dict['swl'].reshape(self.ODOC_dict['swl'].shape[0], -1)
         self.hydro['jswl'] = self.ODOC_dict['jswl'].reshape(self.ODOC_dict['jswl'].shape[0], -1)
         self.hydro['jr'] = self.ODOC_dict['jr'].reshape(self.ODOC_dict['jr'].shape[0], -1)

         num_steps = len(list(self.OSETUP_dict.keys()))

         if 'slprun' in list(self.ODOC_dict.keys()):
             self.hydro['slprun'] = self.ODOC_dict['slprun'].reshape(self.ODOC_dict['jr'].shape[0], -1)
             self.hydro['x1run'] = self.ODOC_dict['x1run'].reshape(self.ODOC_dict['jr'].shape[0], -1)
             self.hydro['x2run'] = self.ODOC_dict['x2run'].reshape(self.ODOC_dict['jr'].shape[0], -1)
             self.hydro['z1run'] = self.ODOC_dict['z1run'].reshape(self.ODOC_dict['jr'].shape[0], -1)
             self.hydro['z2run'] = self.ODOC_dict['z2run'].reshape(self.ODOC_dict['jr'].shape[0], -1)
         else:
             self.hydro['slprun'] = np.zeros([num_steps, 1]) * np.nan
             self.hydro['x1run'] = np.zeros([num_steps, 1]) * np.nan
             self.hydro['x2run'] = np.zeros([num_steps, 1]) * np.nan
             self.hydro['z1run'] = np.zeros([num_steps, 1]) * np.nan
             self.hydro['z2run'] = np.zeros([num_steps, 1]) * np.nan

         # from OSETUP
         time_end = np.zeros([num_steps, 1]) * np.nan
         x = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         setup = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         depth = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         sigma = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         Hs = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         # from OXVELO
         x_xvelo = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         umean = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         ustd = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         # from OYVELO
         x_yvelo = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         stheta = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         vmean = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         vstd = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan

         for ii in range(0, num_steps):
             # OSETUP
             temp_dict_setup = self.OSETUP_dict['hydro%s' % str(ii + 1)]
             time_end[ii] = temp_dict_setup['time_end']
             x[ii] = temp_dict_setup['x']
             setup[ii] = temp_dict_setup['setup']
             depth[ii] = temp_dict_setup['depth']
             sigma[ii] = temp_dict_setup['sigma']
             Hs[ii] = temp_dict_setup['Hs']
             # OXVELO
             temp_dict_xvel = self.OXVELO_dict['hydro%s' % str(ii + 1)]
             x_xvelo[ii] = temp_dict_xvel['x_xvelo']
             umean[ii] = temp_dict_xvel['umean']
             ustd[ii] = temp_dict_xvel['ustd']
             # OYVELO - so, unlike Brad, I define this regardless, it just has nans everywhere if it is empty
             temp_dict_yvel = self.OYVELO_dict['hydro%s' % str(ii + 1)]
             x_yvelo[ii] = temp_dict_yvel['x_yvelo']
             stheta[ii] = temp_dict_yvel['stheta']
             vmean[ii] = temp_dict_yvel['vmean']
             vstd[ii] = temp_dict_yvel['vstd']

         self.hydro['time_end'] = time_end
         self.hydro['x'] = x
         self.hydro['mwl'] = setup
         self.hydro['depth'] = depth
         self.hydro['sigma'] = sigma
         self.hydro['Hs'] = Hs
         self.hydro['x_xvelo'] = x_xvelo
         self.hydro['umean'] = umean
         self.hydro['ustd'] = ustd
         self.hydro['x_yvelo'] = x_yvelo
         self.hydro['stheta'] = stheta
         self.hydro['vmean'] = vmean
         self.hydro['vstd'] = vstd

     def gatherCSHORE_sed(self):
         self.sed = {}
         num_steps = len(list(self.OSETUP_dict.keys()))


         time_end = np.zeros([num_steps, 1]) * np.nan
         x_cross = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         qbx = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         qsx = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         qx = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         # from OLONGS
         x_long = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         qby = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         qsy = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         qy = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         # from OBSUSL
         x_susl = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         ps = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         pb = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         vs = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan

         if self.ODOC_dict['iprofl'] == 1:
             for ii in range(0, num_steps):
                 # OCROSS
                 temp_dict_cross = self.OCROSS_dict['sed%s' % str(ii + 1)]
                 time_end[ii] = temp_dict_cross['time_end']
                 x_cross[ii] = temp_dict_cross['x_cross']
                 qbx[ii] = temp_dict_cross['qbx']
                 qsx[ii] = temp_dict_cross['qsx']
                 qx[ii] = temp_dict_cross['qx']
                 # OLONGS
                 if 'sed1' in list(self.OLONGS_dict.keys()):
                     temp_dict_long = self.OLONGS_dict['sed%s' % str(ii + 1)]
                     x_long[ii] = temp_dict_long['x_long']
                     qby[ii] = temp_dict_long['qby']
                     qsy[ii] = temp_dict_long['qsy']
                     qy[ii] = temp_dict_long['qy']
                 # OBSUSL
                 temp_dict_susl = self.OBSUSL_dict['sed%s' % str(ii + 1)]
                 x_susl[ii] = temp_dict_susl['x_susl']
                 ps[ii] = temp_dict_susl['ps']
                 pb[ii] = temp_dict_susl['pb']
                 vs[ii] = temp_dict_susl['vs']

         self.sed['time_end'] = time_end
         self.sed['x_cross'] = x_cross
         self.sed['qbx'] = qbx
         self.sed['qsx'] = qsx
         self.sed['qx'] = qx
         self.sed['x_long'] = x_long
         self.sed['qby'] = qby
         self.sed['qsy'] = qsy
         self.sed['qy'] = qy
         self.sed['x_susl'] = x_susl
         self.sed['ps'] = ps
         self.sed['pb'] = pb
         self.sed['vs'] = vs

     def gatherCSHORE_veg(self):
         self.veg = {}
         if self.readIF_dict['iveg'] == 1:
             self.veg['n'] = self.readIF_dict['veg_n']
             self.veg['dia'] = self.readIF_dict['veg_dia']
             self.veg['ht'] = self.readIF_dict['veg_ht']
             self.veg['rod'] = self.readIF_dict['veg_rod']
         else:
             self.veg['n'] = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             self.veg['dia'] = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             self.veg['ht'] = np.zeros(self.ODOC_dict['nbinp']) * np.nan
             self.veg['rod'] = np.zeros(self.ODOC_dict['nbinp']) * np.nan

     def gatherCSHORE_morpho(self):
         self.morpho = {}
         num_steps = len(list(self.OSETUP_dict.keys()))

         time = np.zeros([num_steps, 1]) * np.nan

         # if 'FIXED' in path:
         new_list = list(range(0, 1))
         # from OBPROF
         x = np.zeros([1, self.ODOC_dict['nbinp']]) * np.nan
         zb = np.zeros([1, self.ODOC_dict['nbinp']]) * np.nan
         zb_p = np.zeros([1, self.ODOC_dict['nbinp']]) * np.nan
         ivegetated = np.zeros([1, self.ODOC_dict['nbinp']]) * np.nan
         if 'MOBILE' in self.workingDirectory:
             new_list = list(range(0, num_steps))
             # from OBPROF
             x = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
             zb = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
             zb_p = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
             ivegetated = np.zeros([num_steps, self.ODOC_dict['nbinp']]) * np.nan
         else:
             'You need to update load_CSHORE_results in inputOutput to accept the version you have specified!'

         for ii in new_list:
             # OBPROF
             temp_dict_prof = self.OBPROF_dict['morph%s' % str(ii + 1)]
             time[ii] = temp_dict_prof['time']
             x[ii] = temp_dict_prof['x']
             zb[ii] = temp_dict_prof['zb']
             if len(temp_dict_prof['zb_p']) > 0:
                 zb_p[ii] = temp_dict_long['zb_p']
             if len(temp_dict_prof['ivegetated']) > 0:
                 ivegetated[ii] = temp_dict_long['ivegetated']

         self.morpho['time'] = time
         self.morpho['x'] = x
         self.morpho['zb'] = zb
         self.morpho['zb_p'] = zb_p
         self.morpho['ivegetated'] = ivegetated

     def gatherCSHORE_meta(self):
         with open(os.path.join(self.workingDirectory, "metadata.pickle"), "rb") as fid:
             self.meta = pickle.load(fid)

     def readAllFiles(self):
         """This function will take the output dictionaries from all these previous read functions and stack all the information
         into 7 output dictionaries selected based on the catagory of information based in each dictionart

         Args:
           path: path to output .txt files

         Returns:
             params (dict):
                 nbinp: -number of nodes in the bathy profile

                 tanphi: - tangent (sediment friction angle - units?)

                 iover: - 0 = no overtopping , 1 = include overtopping

                 iprofl: - toggle to run morphology (0 = no morph, 1 = morph)

                 effB: - suspension efficiency due to breaking eB (what is this?)

                 ilab: - controls the boundary condition timing. Don't change.  BRAD SAID TO CHANGE THIS TO 1!!!!!!

                 blp: - bedload parameter (what is this?)

                 num_steps: - number of time-steps in the model

                 header: - string that makes up the header of the cshore infile.txt

                 iperm: - 0 = no permeability, 1 = permeable

                 effF: - suspension efficiency due to friction ef (what is this?)

                 isedav: - 0 = unlimited sand, 1 = hard bottom

                 gamma: - shallow water ratio of wave height to water depth (wave breaking parameter?)

                 iveg: - 1 = include vegitation effect (I'm assuming)

             bc (dict):
                 angle_offshore: - wave angle at the offshore boundary at each time-step

                 wave_setup_offshore: - wave setup at the offshore boundary at each time-step

                 Hs_offshore: - wave height at the offshore boundary at each time-step

                 time_offshore: - time of each model time-step in seconds elapsed since model start time

                 Tp_offshore: - wave period at the offshore boundary at each time-step

                 strm_tide_offshore: - water level at the offshore boundary at each time-step

             veg(dict):
                 rod: - vegitation erosion limit below sand for failure (what is this?!?!?)

                 dia: - vegetation dia. (units ??!?!?!?!?)

                 ht: - vegetation height (units?!?!?!?!)

                 n: - vegetation density (units?!?!?!?!)

             hydro(dict):
                 stheta: - sine of the wave angle (theta) for each time step

                 jdry: - the most landward node in the wet/dry region

                 time_end: - i think this is the time at the end of each model time step in seconds after model start

                 x_xvelo: - the tech report we got from Brad does not mention this variable in its discussion of OXVELO

                 umean: - mean cross-shore velocity at each node and time-step of the simulation

                 jswl: -index of the node at the still water shoreline

                 swl: - I am going to guess based on Brad's Tech Note that this is the still water level?

                 x2run: - i think this is just the x-position of each node for the second of two bottom profiles (if you gave it two bottom profiles)?  This guess is just based on Brad's Tech report

                 Hs: - wave height at each node and time-step of the simulation

                 slprun: - representative bottom slope in the swash zone

                 x1run: -i think this is just the x-position of each node for the first of two bottom profiles (if you gave it two bottom profiles)?  This guess is just based on Brad's Tech report

                 vstd: - standard deviation of the alongshore velocity at each node and time-step of the simulation

                 mwl: - mean water level at each node and time-step

                 vmean: - mean alongshore velocity at each node and time-step

                 z1run: -i think this is just the elevation of each node for the first of two bottom profiles (if you gave it two bottom profiles)?  This guess is just based on Brad's Tech report

                 x_yvelo: -the tech report we got from Brad does not mention this variable in its discussion of OYVELO or OXVELO

                 runup_2_percent: - 2 percent exceedance run-up elevation at each time-step

                 jr: - i think this is just the number of nodes in your cross-section bottom boundary?

                 runup_mean: - mean runup elevation at each time-step

                 ustd: -standard deviation of the cross-hore velocity at each node and time-step of the simulation

                 depth: - water depth at each node and time-step

                 x: - x-position of each node in model coordinates

                 sigma: - standard deviation of the water surface elevation for each time-step in the model run

                 z2run: -i think this is just the elevation of each node for the second of two bottom profiles (if you gave it two bottom profiles) - needs to be checked

             sed (dict):
                 ps: - probability of self.sediment suspension

                 x_susl: - this variable is not mentioned in Brad's Tech Report.  if i had to guess i would say it is just the x-position of each node

                 qbx: - bed load sediment transport in cross-shore direction

                 qx: - total sediment transport in cross-shore direction

                 vs: - suspended sediment volume per unit horizontal bottom area

                 time_end: - i think this is the time at the end of each model time step in seconds after model start

                 x_cross: -this variable is not mentioned in Brad's Tech Report.  if i had to guess i would say it is just the x-position of each node

                 pb: - probability of sediment movement

                 qy: - total sediment transport in the alongshore direction

                 qby: - bed load sediment transport in the alongshore direction

                 x_long: - this variable is not mentioned in Brad's Tech Report.  if i had to guess i would say it is just the x-position of each node

                 qsy: - suspended load sediment transport in the alongshore direction

                 qsx: - suspended load sediment transport in the cross-shore direction

             morpho (dict):
                 ivegetated: - which nodes are vegetated or not

                 x: - x-position of each node in the model

                 zb_p: - vertical coordinate of the lower boundary of the permeable layer

                 zb: - bottom elevation of each node at each time-step of the simulation

                 time: - i think this is the time at the end of each model time step in seconds after model start

             meta (dict):
                 bathy_survey_num: - survey number that the initial bathymetry was taken from

                 bathy_prof_num: - profileLine number that makes up the initial cshore bathy

                 blank_wave_data: - which wave data were interpolated to generate the input file

                 BC_gage: - name of the wave gage used as the BC for this cshore run

                 fric_fac: - this is the friction factor that is set automatically in the infile generation script

                 BC_FRF_Y: - this is the yFRF location of the BC wave gage.

                 BC_FRF_X: - this is the cFRF location of the BC wave gage.  I think this is rounded down to the nearest 1 m

                 startTime: - start time for this particular cshore model run

                 bathy_surv_stime: - this is the start time of the bathymetry survey that was used in the model

                 bathy_y_sdev: - this is the standard deviation of the actualy yFRF positions of each point in the survey used in the model

                 version: - MOBILE, MOBILE_RESET or FIXED right now

                 timerun: - duration that each individual simulation was run.  24 hours unless specified otherwise

                 dx: - grid spacing in the model. default is 1 m unless specified otherwise

                 time_step: - model time-step.  1 hour unless specified otherwise

         """

         self.readCSHORE_ODOC()
         self.readCSHORE_infile()
         self.readCSHORE_OBPROF()
         self.readCSHORE_OSETUP()
         self.readCSHORE_OXVELO()
         self.readCSHORE_OYVELO()
         self.readCSHORE_OCROSS()
         self.readCSHORE_OLONGS()
         self.readCSHORE_OBSUSL()

         # all this does is take the dicts I created from my output text files a reformats them
         # params

         self.gatherCSHORE_params()
         self.gatherCSHORE_bc()
         self.gatherCSHORE_waves()
         self.gatherCSHORE_hydro()
         self.gatherCSHORE_sed()
         self.gatherCSHORE_veg()
         self.gatherCSHORE_morpho()
         self.gatherCSHORE_meta()

         spatialData = self._resultsToDict()
         pointData = None
         return spatialData, pointData


