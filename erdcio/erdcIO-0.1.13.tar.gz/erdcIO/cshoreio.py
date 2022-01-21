import numpy as np
import datetime as DT
import warnings, glob, os, shutil
import pickle as pickle
import netCDF4 as nc
import f90nml
import collections
from subprocess import check_output

from testbedutils import dirtLib
from erdcIO import base

class cshoreio(base):
    def __init__(self, workingDirectory, testName, **kwargs):
        """

        Args:
            fileNameBase:
            **kwargs:
        """
        self.modelName = 'cshore'  # model name needs to be before base init (used in base init)
        super(cshoreio, self).__init__(workingDirectory, testName, **kwargs)
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
            'iline': self.newModelParams.get('iline', 1),  # single line
            'iprofl': self.newModelParams.get('iprofl', 0),  # 0 = no morph, 1 = run morph
            'isedav': self.newModelParams.get('iseday', 0),  # 0 = unlimited sand, 1 = hard bottom
            'iperm': self.newModelParams.get('iperm', 0),  # 0 = no permeability, 1 = permeable
            'iover': self.newModelParams.get('iover', 1),  # 0 = no overtopping , 1 = include overtopping
            'infilt': self.newModelParams.get('infilt', 0),  # 1 = include infiltration landward of dune crest
            'iwtran': self.newModelParams.get('iwtran', 0),
            # 0 = no standing water landward of crest, 1 = wave transmission due to overtopping
            'ipond': self.newModelParams.get('ipond', 0),  # 0 = no ponding seaward of SWL
            'iwcint': self.newModelParams.get('iwcint', 0),  # 0 = no W & C interaction , 1 = include W & C interaction
            'iroll': self.newModelParams.get('iroll', 0),  # 0 = no roller, 1 = roller
            'iwind': self.newModelParams.get('iwind', 0),  # 0 = no wind effect'
            'itide': self.newModelParams.get('itide', 0),  # 0 = no tidal effect on currents
            'iveg': self.newModelParams.get('iveg', 0),  # 1 = include vegitation effect
            'veg_Cd': self.newModelParams.get('veg_Cd', 1),  # vegitation drag coeff
            'veg_n': self.newModelParams.get('veg_n', 100),  # vegitation density (units?)
            'veg_dia': self.newModelParams.get('veg_dia', 0.01),  # vegitation diam (units? mean or median?)
            'veg_ht': self.newModelParams.get('veg_ht', 0.20),  # vegitation height (units? mean or median?)
            'veg_rod': self.newModelParams.get('veg_rod', 0.1),  # vegitation erosion limit below sand for failure
            'veg_extent': self.newModelParams.get('veg_extend', np.array([.7, 1])),
            # vegitation coverage as fraction of total domain length
            'gamma': self.newModelParams.get('gamma', 0.72),  # shallow water ratio of wave height to water depth
            'sporo': self.newModelParams.get('sporo', 0.4),  # sediment porosity
            'd50': self.newModelParams.get('d50', 0.15),  # d_50 in mm
            'sg': self.newModelParams.get('sg', 2.65),  # specific gravity of the sand grains
            'effb': self.newModelParams.get('effb', 0.002),  # suspension efficiency due to breaking eB
            'efff': self.newModelParams.get('efff', 0.004),  # suspension efficiency due to friction ef
            'slp': self.newModelParams.get('slp', 0.5),  # suspended load parameter
            'slpot': self.newModelParams.get('slpot', 0.1),  # overtopping suspended load parameter
            'tanphi': self.newModelParams.get('tanphi', 0.630),  # tangent (sediment friction angle - units?)
            'blp': self.newModelParams.get('blp', 0.002),  # bedload parameter
            'rwh': self.newModelParams.get('rwh', 0.01),  # numerical rununp wire height
            'ilab': self.newModelParams.get('ilab', 1)
        }
        # controls the boundary condition timing. 1 uses time average while 0 requires an extra input step and solves between input-times .
        # 'fric_fac': meta_dict['fric_fac']}  # bottom friction factor

    def _generateRunStrings(self, modelExecutable):

        # preprocess string
        self.runString = '{} > infile.out'.format(modelExecutable)

    def _resultsToDict(self):

        return {'params': self.params, 'bc': self.bc, 'hydro': self.hydro, 'sed': self.sed, 'veg': self.veg,
                'morpho': self.morpho, 'meta': self.meta}

    def setCSHORE_time(self, timeStep):
        self.timeStep = timeStep
        simDuration = self.endTime - self.startTime
        self.simDuration = simDuration.total_seconds() / 3600

        self.reltime = np.arange(0, simDuration.total_seconds() + timeStep, timeStep)

    def readCSHORE_nml(self, nmlname='namelist.nml'):

        # ofname = os.path.join(self.workingDirectory, nmlname)  # model required file name

        if os.path.isfile(nmlname):
            nml = f90nml.read(nmlname)

            self.newModelParams = nml['infile'].todict()

            self._replaceDefaultParams()

    def makeCSHORE_meta(self, bathyDict, waveDict, wlDict=None, ctdDict=None, dx=1, fric_fac=0.015, version='MOBILE',
                        **kwargs):

        startTime = kwargs.get('startTime', self.startTime)
        simDuration = kwargs.get('simDuration', self.simDuration)
        timeStep = kwargs.get('timeStep', self.timeStep)

        self.meta_dict = {'startTime': startTime, 'timerun': simDuration, 'time_step': timeStep, 'dx': dx,
                          'fric_fac': fric_fac, 'version': version, 'bathy_surv_num': bathyDict['bathy_surv_num'],
                          'bathy_surv_stime': bathyDict['bathy_surv_stime'],
                          'bathy_surv_etime': bathyDict['bathy_surv_etime'],
                          'bathy_prof_num': bathyDict['bathy_prof_num'],
                          'bathy_y_max_diff': bathyDict['bathy_y_max_diff'], 'bathy_y_sdev': bathyDict['bathy_y_sdev'],
                          'BC_FRF_X': bathyDict['BC_FRF_X'], 'BC_FRF_Y': bathyDict['BC_FRF_Y'],
                          'BC_gage': waveDict['BC_gage'], 'blank_wave_data': waveDict['blank_wave_data'],
                          'blank_wl_data': wlDict['flag']}

    def makeCSHORE_bc(self, bathyDict, waveDict, wlDict=None, ctdDict=None, **kwargs):
        reltime = kwargs.get('reltime', self.reltime)

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

        self.infile['header'] = ['------------------------------------------------------------',
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
            fid.write(
                '%11.4f%11.4f%11.4f         ->D50 WF SG\n' % (self.infile['d50'], self.infile['wf'], self.infile['sg']))
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
                    self.BC_dict['timebc_wave'][ii], self.BC_dict['Tp'][ii],
                    (np.sqrt(2) / 2.0) * self.BC_dict['Hs'][ii],
                    self.BC_dict['Wsetup'][ii], self.BC_dict['swlbc'][ii], self.BC_dict['angle'][ii]))
        else:
            fid.write('%-8i                                  ->NWAVE \n' % int(self.infile['nwave'] - 1))
            fid.write('%-8i                                  ->NSURGE \n' % int(self.infile['nsurg'] - 1))
            for ii in range(0, len(self.BC_dict['Hs'])):
                fid.write('%11.2f%11.4f%11.4f%11.4f\n' % (
                    self.BC_dict['timebc_wave'][ii], self.BC_dict['Tp'][ii],
                    (np.sqrt(2) / 2.0) * self.BC_dict['Hs'][ii],
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
                if self.BC_dict['x'][ii] >= np.max(self.BC_dict['x']) * self.infile['veg_extent'][0] and \
                        self.BC_dict['x'][ii] <= np.max(
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

        self.newModelParams = kwargs.get('newModelParams', {})  # hold dictionary for updates to
        self.versionPrefix = kwargs.get('versionPrefix', self.versionPrefix)

        if not os.path.isdir(self.workingDirectory):
            os.mkdir(self.workingDirectory)

        if self.generateFiles is True:
            # self.readCSHORE_nml()
            self._replaceDefaultParams()  # double check we're replacing the parameters appropritely

            self.makeCSHORE_meta(bathyPacket, wavePacket, wlDict=wlPacket, ctdDict=ctdPacket,
                                 version=self.versionPrefix)

            self.makeCSHORE_bc(bathyPacket, wavePacket, wlDict=wlPacket, ctdDict=ctdPacket)

            self.writeCSHORE_infile()

    def runSimulation(self, modelExecutable=None, hotStartDirectory=None):
        if self.runFlag is True:
            # generate appropriate run strings
            self._generateRunStrings(modelExecutable)
            # check appropriate data are in place
            # self._preprocessCheck()

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
    # with open(self.pickleSaveName, 'wb') as fid:
    #    pickle.dump(self, fid, protocol=pickle.HIGHEST_PROTOCOL)
    # else:
    # print('I might be doing something wrong by loading and re-assigning self!!!!')
    # with open(self.pickleSaveName, 'rb') as fid:
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

    def readCSHORE_infile(self, fname=None):
        """This function will read the CSHORE infile

        Args:
          path: path to input file

        Returns:
            relevant variables in an INFILE dictionary.
        """
        if fname:
            with open(fname, 'r') as fid:
                tot = fid.readlines()
        else:
            with open(self.workingDirectory + '/infile', 'r') as fid:
                tot = fid.readlines()
        fid.close()
        tot = np.asarray([s.strip() for s in tot])

        vars = ['ILINE', 'IPROFL', 'IPERM', 'IOVER', 'IWTRAN', 'IPOND', 'IWCINT', 'IROLL',
                'IWIND', 'ITIDE', 'IVEG', 'DXC', 'GAMMA', 'RWH', 'ILAB']

        # blah = 'ISEDAV', 'INFILT',

        self.readIF_dict = {}
        self.readBC_dict = {}
        self.readBT_dict = {}

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
            self.readIF_dict['sg'] = float(dummyVar[2])

            # EFFB and EFFF
            row_ind = np.asarray(np.argwhere(['EFFB' in s for s in tot])).flatten()
            row = tot[row_ind[0]]
            dummyVar = row[0:row.find('-') - 1].split()
            self.readIF_dict['effb'] = float(dummyVar[0])
            self.readIF_dict['efff'] = float(dummyVar[1])
            self.readIF_dict['slp'] = float(dummyVar[2])
            # BLP and TANPHI
            row_ind = np.asarray(np.argwhere(['BLP' in s for s in tot])).flatten()
            row = tot[row_ind[0]]
            dummyVar = row[0:row.find('-') - 1].split()
            self.readIF_dict['tanphi'] = float(dummyVar[0])
            self.readIF_dict['blp'] = float(dummyVar[1])
            # ILAB
            # row_ind = np.asarray(np.argwhere(['ILAB' in s for s in tot])).flatten()
            # row = tot[row_ind[0]]
            # row[0:row.find('-') - 1]
            # self.readIF_dict['ilab'] = float(row[0:row.find('-') - 1])

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

        row = tot[row_ind_2[0]]
        nbathy = float(row[0:row.find('-') - 1])
        rows = tot[row_ind_2[0] + 1:]
        num_pts = len(rows)
        x = np.zeros(num_pts)
        z = np.zeros(num_pts)
        fw = np.zeros(num_pts)
        for ii in range(0, len(rows)):
            dummyVar = rows[ii].split()
            x[ii] = dummyVar[0]
            z[ii] = dummyVar[1]
            fw[ii] = dummyVar[2]
        self.readIF_dict['x'] = x
        self.readIF_dict['zb'] = z
        self.readIF_dict['fw'] = fw

    def createCSHORE_dicts(self):

        vars = ['ILINE', 'IPROFL', 'IPERM', 'IOVER', 'IWTRAN', 'IPOND', 'IWCINT', 'IROLL',
                'IWIND', 'ITIDE', 'IVEG', 'DXC', 'GAMMA', 'RWH', 'ILAB']
        modelParams = {}
        for vv in vars:
            modelParams[vv.lower()] = self.readIF_dict[vv.lower()]

        if self.readIF_dict['iprofl'] == 1:
            vars = ['D50', 'WF', 'SG', 'EFFB', 'EFFF', 'SLP', 'TANPHI', 'BLP']
            for vv in vars:
                modelParams[vv.lower()] = self.readIF_dict[vv.lower()]

        waves = {}
        waves['BC_gage'] = 'Unknown'
        waves['blank_wave_data'] = None
        waves['Hs'] = self.readIF_dict['Hs_bc']
        waves['Tp'] = self.readIF_dict['Tp_bc']
        waves['angle'] = self.readIF_dict['angle_bc']
        waves['lon'] = 0.0
        waves['lat'] = 0.0

        wl_data = {}
        wl_data['time'] = self.readIF_dict['time_offshore']
        wl_data['avgWL'] = self.readIF_dict['wl_bc']
        wl_data['flag'] = 0
        wl_data['name'] = ' '

        bathy = {}
        bathy['bathy_surv_num'] = 0
        bathy['bathy_surv_stime'] = 0
        bathy['bathy_surv_etime'] = 0
        bathy['bathy_prof_num'] = 0
        bathy['bathy_y_max_diff'] = 0
        bathy['bathy_y_sdev'] = 0
        bathy['BC_FRF_X'] = 0
        bathy['BC_FRF_Y'] = 0
        bathy['x'] = self.readIF_dict['x']
        bathy['zb'] = self.readIF_dict['zb']
        bathy['fw'] = self.readIF_dict['fw']

        return modelParams, waves, wl_data, bathy

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
        if self.readIF_dict['iprofl'] == 0:
            new_list = list(range(0, 1))
        elif self.readIF_dict['iprofl'] == 1:
            new_list = list(range(0, len(self.readIF_dict['time_offshore'])))
        else:
            print('You need to update read_CSHORE_OBPROF in inputOutput to accept the version you have specified!')
        #print(new_list)
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

        if self.readIF_dict['ilab'] == 0:
            lensim = len(self.readIF_dict['time_offshore']) - 1
        else:
            lensim = len(self.readIF_dict['time_offshore'])
        for ii in range(0,lensim):
            self.OSETUP_dict['hydro%s' % str(ii + 1)] = {}
            row1 = tot[ind_track]

            if float(row1.split()[0]) == 1:
                N = int(row1.split()[1])
                tme = float(row1.split()[-1])
            else:
                N = int(row1.split()[0])

            dum = tot[ind_track + 1:ind_track + 1 + N + 1]  #Not sure about this extra +1
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

        if self.readIF_dict['ilab'] == 0:
            lensim = len(self.readIF_dict['time_offshore']) - 1
        else:
            lensim = len(self.readIF_dict['time_offshore'])
        for ii in range(0, lensim):
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
        self.hydro['time'] = self.readIF_dict['time_offshore']
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
            if ii == 0:
                x = temp_dict_setup['x']  # x does not change in time.
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
        if self.infile['iprofl'] == 1:
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