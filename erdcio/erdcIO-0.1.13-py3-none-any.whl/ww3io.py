import numpy as np
import datetime as DT
import warnings, glob, os, shutil
import pickle as pickle
import netCDF4 as nc
import f90nml
import collections
from subprocess import check_output

from erdcIO import base


class ww3io(base):
    def __init__(self, workingDirectory, testName, **kwargs):
        """

        Args:
            fileNameBase:
            **kwargs:
        """
        self.modelName = 'ww3'  # model name needs to be before base init (used in base init)
        super(ww3io, self).__init__(workingDirectory, testName, **kwargs)
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
        self.ww3bounc = {'BOUND_NML': {}}
        self.ww3bounc['BOUND_NML']['BOUND%Mode'] = self.newModelParams.pop('boundaryMode', 'WRITE')
        self.ww3bounc['BOUND_NML']['BOUND%Interp'] = self.newModelParams.pop('boundaryInterp', 2)
        self.ww3bounc['BOUND_NML']['BOUND%Verbose'] = self.newModelParams.pop('boundaryVerbose', 1)
        self.ww3bounc['BOUND_NML']['BOUND%File'] = self.newModelParams.pop('boundaryfile', 'spec.list')

        # writeWW3_grid
        self.ww3grid = collections.OrderedDict()
        self.ww3grid['SPECTRUM_NML'] = {}
        self.ww3grid['SPECTRUM_NML']['SPECTRUM%XFR'] = self.newModelParams.pop('spectrumXFR',
                                                                               1.1)  # set by def, written by input spec gen
        self.ww3grid['SPECTRUM_NML']['SPECTRUM%FREQ1'] = self.newModelParams.pop('sepctrumFREQ1',
                                                                                 0.038)  # set by def, written by input spec gen
        self.ww3grid['SPECTRUM_NML']['SPECTRUM%NK'] = self.newModelParams.pop('spectrumNK', 35)  # sets NKI
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
        self.ww3grid['GRID_NML']['GRID%COORD'] = self.newModelParams.pop('gridCOORD', 'SPHE')  # or CART
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
        # self.ww3grid = collections.OrderedDict()

        # self.IOSTYP = self.newModelParams.pop('ISOTYP', 1)
        # self.outputInterval = self.newModelParams.pop('outputInterval', 1800)  # 30 min default
        # self.outputVarString = self.newModelParams.pop('outputVarString', "HS LM T02 T01 DIR UST CHA CGE DTD FC CFX CFD")
        # self.homogeneousWinds = self.newModelParams.pop('homogeneousWinds', 'T')
        # self.homogeneousWLs = self.newModelParams.pop('homogeneousWLs', 'T')

        # writeWW3_ounf
        # self.fieldTimeStart = self.newModelParams.pop('fieldTimeStart', DT.datetime.strptime(os.path.basename(
        #                                        self.workingDirectory),  self.dateStringFmt).strftime('%Y%m%d %H%M%S'))
        # self.fieldTimeStride = self.newModelParams.pop('fieldTimeStride',  3600)

        # writeWW3_ounp
        # self.pointTimeStart = self.newModelParams.pop('pointTimeStart', DT.datetime.strptime(os.path.basename(
        #                         self.workingDirectory),  self.dateStringFmt).strftime('%Y%m%d %H%M%S'))
        # self.pointTimeStride = self.newModelParams.pop('pointTimeStride', 3600)
        for key in self.newModelParams.keys():
            warnings.warn('{} is NOT USED, please see wrr._replaceDefaultParams for help'.format(key))
        # if self.newModelParams.keys().any():
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
        self.simulationCoreCount = np.floor(self.nodeCount / 500).astype(int)  # 5oo grid nodes per core
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
            self.dateString, self.dateStringFmt).strftime('%Y%m')))
        pointfname = os.path.join(self.workingDirectory, "ww3.{}_spec.nc".format(DT.datetime.strptime(
            self.dateString, self.dateStringFmt).strftime('%Y%m')))
        meshfname = os.path.join(self.workingDirectory, self.fNameBase + '.msh')

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

    def _processStationData(self, pointNc):
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
        timing = DT.datetime(2021, 1, 1, 6, 0, 0)
        self.write_pbs('ww3', timing, runtext)

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

        f90nml.write(self.ww3bounc, ofname, force=True)

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

    def create_bound(self, grid_inbindfname):
        # could come up with logic for boundaries that are continuous
        with open(grid_inbindfname, 'r') as fid:
            nodes = fid.read().splitlines()
        nodeCount = np.size(nodes)
        self.ww3grid['INBND_COUNT_NML'] = {}
        self.ww3grid['INBND_COUNT_NML']['INBND_COUNT%N_POINT'] = nodeCount
        self.ww3grid['INBND_POINT_NML'] = collections.OrderedDict()
        for ii, nn in enumerate(nodes):
            n = nn.split()
            self.ww3grid['INBND_POINT_NML']['INBND_POINT(' + str(ii + 1) + ')'] = [int(n[0]), int(n[1]), False]

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

        ofname = kwargs.get('ofname', os.path.join(self.workingDirectory, 'ww3_grid.nml'))  # ww3 model assumes fname

        # alphabetical order: see self._replaceDefaultParams for setting of these values

        # load points for inbnd writing (boundary points)
        if grid_inbindfname is not None:
            self.create_bound(grid_inbindfname)

        f90nml.write(self.ww3grid, ofname, force=True)

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
        f90nml.write(self.ww3nml, ofname, force=True)

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

    def set_homogeneous(self, homog):
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

    def set_homogenous_values(self, key, packet):
        startvalue = 0
        if self.hotStartFlag:
            startvalue = 1
        self.ww3shel['HOMOG_COUNT_NML']['HOMOG_COUNT%N_' + key] = len(packet['time']) - startvalue

        for ii in range(startvalue, len(packet['time'])):
            nn = ii + 1 + self.hhstart - startvalue
            self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT(' + str(nn) + ')%NAME'] = key
            self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT(' + str(nn) + ')%DATE'] = DT.datetime.strftime(
                packet['time'][ii], '%Y%m%d %H%M%S')
            if key == 'WND':
                self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT(' + str(nn) + ')%VALUE1'] = round(packet['avgspd'][ii], 2)
                self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT(' + str(nn) + ')%VALUE2'] = round(packet['avgdir'][ii], 1)
            elif key == 'LEV':
                self.ww3shel['HOMOG_INPUT_NML']['HOMOG_INPUT(' + str(nn) + ')%VALUE1'] = round(packet['avgWL'][ii], 2)

        self.hhstart = + len(packet['time']) - startvalue

    def writeWW3_points(self):
        """Writes points.list file from self.savePoints

        Args:
            None

        Keyword Args:
            'ofname'(str): output file name, (default=self.workingDirectory + 'points.list')

        Returns:

        """

        ofname = os.path.join(self.workingDirectory, 'points.list')  # model required file name
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
        ofname = os.path.join(self.workingDirectory, 'ww3_shel.nml')  # model required file name

        startTime_w = startTime.strftime('%Y%m%d %H%M%S')  # yyyymmdd hhmmss format.
        endTime_w = endTime.strftime('%Y%m%d %H%M%S')  # yyyymmdd hhmmss format.

        # set which outputs to include
        type6 = kwargs.get('type6', False)  # wave system decomposition output
        # include other output file types here

        # variables
        IOSTYP = kwargs.get('ISOTYP', 1)
        # outputInterval = self.outputInterval    # kwargs.get('outputInterval', 1800)  # 30 min default
        # outputVarString = self.outputVarString  # kwargs.get('outputVarString', "HS LM T02 T01 DIR UST CHA CGE DTD FC "
        #                               "CFX CFD")
        # homoWinds = self.homogeneousWinds       # kwargs.get('homogeneousWinds', 'T')
        # homoWLs = self.homogeneousWLs           # kwargs.get('homogeneousWLs', 'T')

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
        self.ww3shel['OUTPUT_DATE_NML']['DATE%RESTART'] = [startTime_w, restint.total_seconds(), endTime_w]

        self.hhstart = 0
        self.ww3shel['HOMOG_COUNT_NML'] = collections.OrderedDict()
        self.ww3shel['HOMOG_INPUT_NML'] = collections.OrderedDict()
        if 'INPUT%FORCING%WINDS' in homog:
            self.set_homogenous_values('WND', windPacket)
        if 'INPUT%FORCING%WATER_LEVELS' in homog:
            self.set_homogenous_values('LEV', wlPacket)
        if 'INPUT%FORCING%CURRENTS' in homog:
            self.set_homogenous_values('CUR', wlPpacket)

        f90nml.write(self.ww3shel, ofname, force=True)

    def writeWW3_ounf(self, startTime, timeStride=1800, **kwargs):
        """Write a ounf file for ww3 post processing.

        The ounf file contains input for post processing of WW3 field data.

        Keyword Args:
            startTime: start time to log data (in datetime format)
            'timeStride': Time stride for the output field (Default=1800)


        Returns:
            None

        """
        ofname = os.path.join(self.workingDirectory, 'ww3_ounf.nml')  # model required file name

        self.ww3ounf = collections.OrderedDict()
        self.ww3ounf['FIELD_NML'] = collections.OrderedDict()
        self.ww3ounf['FIELD_NML']['FIELD%TIMESTART'] = startTime.strftime('%Y%m%d %H%M%S')
        self.ww3ounf['FIELD_NML']['FIELD%TIMESTRIDE'] = '{}'.format(timeStride)
        self.ww3ounf['FIELD_NML']['FIELD%LIST'] = 'HS LM T02 T01 DIR UST CHA CGE DTD FC CFX CFD'
        self.ww3ounf['FIELD_NML']['FIELD%SAMEFILE'] = True
        self.ww3ounf['FIELD_NML']['FIELD%TYPE'] = 4
        self.ww3ounf['FIELD_NML']['FIELD%TIMECOUNT'] = '1000000000'
        self.ww3ounf['FIELD_NML']['FIELD%TIMESPLIT'] = 6
        self.ww3ounf['FIELD_NML']['FIELD%PARTITION'] = '0 1 2 3'

        self.ww3ounf['FILE_NML'] = collections.OrderedDict()
        self.ww3ounf['FILE_NML']['FILE%PREFIX'] = 'ww3.'
        self.ww3ounf['FILE_NML']['FILE%NETCDF'] = 4

        f90nml.write(self.ww3ounf, ofname, force=True)

    def writeWW3_ounp(self, startTime, timeStride=1800, otype=1, param=1, **kwargs):
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
        ofname = os.path.join(self.workingDirectory, 'ww3_ounp.nml')  # model required file name

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

        f90nml.write(self.ww3ounp, ofname, force=True)

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
        # -------------------------------------------------------------------------------
        f = open(outFname, 'w+')
        f.write('$MeshFormat\n{} {} {}\n$EndMeshFormat\n'.format(gmeshVersion, 0, 8))
        # nodes are points, have values

        f.write('$Nodes\n{}\n'.format(points.shape[0]))
        for ll, line in enumerate(points):
            f.write('{0:>10}{1: >30}{2: >30}{3: >30}\n'.format(ll + 1, line[0], line[1], line[2]))
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

    def setHotStart(self, hotStartDirectory, gridName='ww3'):

        try:
            rfiles = np.sort(glob.glob(os.path.join(hotStartDirectory, 'restart*' + gridName)))
            shutil.copyfile(rfiles[-1], os.path.join(self.workingDirectory, 'restart.' + gridName))
            print("Move restart files into working directory")
        except:
            print("No restart file available for {}".format(gridName))

    def writeAllFiles(self, bathyPacket=None, wavePacket=None, windPacket=None, wlPacket=None, gridfname=None,
                      gridtype='unstr', updateBathy=True, hotStartDirectory=None, **kwargs):
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
            self._check_input()  # check to make sure all of my data are appropriately in place
            self.savePoints = kwargs.get('savePoints', self.savePoints)

            print('writing all {} input files '.format(self.modelName))
            specFname = self.writeWW3_spec(wavePacket)  # write individual spec file

            # write grid file

            scaleFac = 1.0  # defines how to scale bathy (negative values flip positive down to positive up)
            gtemp = gridfname.rfind('.')
            self.writeWW3_grid(grid_inbindfname=gridfname[:gtemp] + '.inbnd',
                               spectrumNTH=wavePacket['spec2d'].shape[2], spectrumNK=wavePacket['spec2d'].shape[1],
                               unstSF=scaleFac)
            if os.path.exists(gridfname[:gtemp] + '.latbnd'):
                shutil.copyfile(gridfname[:gtemp] + '.latbnd', os.path.join(self.workingDirectory, 'meshbnd.msh'))

            # write mesh file
            # ww3io.writeWW3_mesh(gridNodes=bathy)                                # write gmesh file using gmsh library
            if updateBathy is True:
                self.write_msh(points=bathyPacket.points,
                               cell_data=bathyPacket.cell_data)  # write gmesh using manual function
            else:
                shutil.copy(gridfname, os.path.join(self.workingDirectory, self.fNameBase + '.msh'))
                self.nodeCount = bathyPacket.cell_data['vertex'].size

            # write name list file -- shouldn't change
            if gridtype == 'unstr':
                self.set_unstructured()

            # copy hotstart file if requested
            if self.hotStartFlag:
                self.setHotStart(hotStartDirectory)

            self.writeWW3_namelist()  # will write with defaults with no input

            # args
            specListFileName = self.writeWW3_speclist(ofname=os.path.join(self.workingDirectory, 'spec.list'),
                                                      specFiles=specFname.rsplit('/')[-1])  # write specFile

            # write files used as spectral boundary
            self.writeWW3_bounc(specListFilename=specListFileName.rsplit('/')[-1])  # write boundary files
            self.writeWW3_shel(self.startTime, self.endTime, windPacket=windPacket, wlPacket=wlPacket,
                               # write shel file
                               outputInterval=1800)
            self.writeWW3_points()  # write the save points

            self.writeWW3_ounf(self.startTime)  # process field save file
            self.writeWW3_ounp(self.startTime)  # process point save file

            # calculate number of cores to run simulation
            self._calculateSimulationCoreCount()

    def writeWW3_pbs(self):
        runtext = ['{}\n'.format(self.runString1), 'wait\n', '{}\n'.format(self.runString2), 'wait\n',
                   '{}\n'.format(self.runString3), 'wait\n', '{}\n'.format(self.runString4), 'wait\n',
                   '{}\n'.format(self.runString5)]

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
                print('Simulation took {:.1f} minutes'.format(self.simulationWallTime.total_seconds() / 60))

                # post process output data
                dt = DT.datetime.now()
                _ = check_output(self.runString4, shell=True)
                _ = check_output(self.runString5, shell=True)
                print(
                    'Simulation postProcess took {:.1f} minutes'.format((DT.datetime.now() - dt).total_seconds() / 60))
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
            fname = os.path.join(self.workingDirectory, self.fNameBase + '.msh')
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
            'cell_data': {'vertex': np.array(boundary),
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
                                                                                                   self.dateStringFmt).strftime(
                '%Y%m')))
        ncfile = nc.Dataset(fileName)  # xr.load_dataset(fileName)
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
                                                                                                        self.dateStringFmt).strftime(
                '%Y%m')))

        ncfile = nc.Dataset(fileName)  # xr.load_dataset(fileName)
        ncdata = {}
        for ii in ncfile.variables:
            ncdata[ii] = ncfile[ii][:]
        ncdata['timeUnits'] = ncfile['time'].units
        return ncdata