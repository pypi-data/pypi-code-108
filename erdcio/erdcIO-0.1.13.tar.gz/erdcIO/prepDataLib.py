"""
Created on Wed Jul 22 08:20:47 2015
This code is meant to serve the already retrieved data from the data server and
return and preprocess  for model running on the Coastal Model Test Bed
@author: Spicer Bak, PhD
"""
import datetime as DT
import glob, os, shutil, time, math, pickle
import numpy as np
from scipy import interpolate
from testbedutils import sblib as sb, geoprocess as gp
import netCDF4 as nc
import numpy.matlib as npmat
from testbedutils import anglesLib
from testbedutils import gridTools
from testbedutils.gridTools import createGridNodesinFRF, convertGridNodesFromStatePlane, CreateGridNodesInStatePlane


class prepDataTools:

    def scalartimeavg(self, trtm, trD, data):
        """This function averages "data" over the timestep by looking averaging
        data between timesteps on a given record (simTimeRcd)  The advantage here is
        that the function will handle missing data in a timestep, by averaging
        the available data in the timestep.

        Args:
          trtm: (Time record to match): a list of datetime formatted timestamps to match
                data for
          trD: (time record data): the timestamp of the input data to be averaged/accounted for
          data: the data to be averaged/accounted for
        
        Returns:
            timeRdcOut: (time record out): record, in datetime format, of the output
                    record
            dataAvgOut: (data avg out) averaged data for the output data

        """

        if np.size(trtm) == 1 and type(trtm) is not list and type(trtm) is not np.ndarray:
            trtm = [trtm]
        assert isinstance(np.array(trD).dtype, float)  == isinstance(np.array(trtm).dtype, float), 'time data types must be the same (for comparison)'
        assert np.size(data) == np.size(trD), 'Time Record (out) does not match Time Record (to match)'
        flagLoc = np.zeros_like(trtm)
        for zz in range(0, np.size(trtm)):  # number of records to match
            if zz == np.size(trtm) - 1:  # if its the last record
                if not (trtm[zz] <= trD).any():  # check to make sure its end of record
                    flagLoc[zz] = np.nan # add nan where to inerpolate
            else:
                if not np.logical_and(trtm[zz] <= trD, trD < trtm[zz + 1]).any():
                    flagLoc[zz] = np.nan

        flagOut = np.isnan(flagLoc)
        #now find nans, interpolate NaN values
        f_x = interpolate.interp1d(trD, data, assume_sorted=True, fill_value='extrapolate')
        dataAvgOut = f_x(trtm)

        # QA/QC plot
        # from matplotlib import pyplot as plt
        # plt.plot(trD, data, 'r.-', label='Data In')
        # plt.plot(trtm, dataAvgOut, 'g:.', label='Data out')
        # plt.legend()
        # plt.savefig('QAQC_scalartimeaverage.png')
        # plt.close()
        assert (np.array(trtm) == np.array(trtm)).all(), '<<EE>> Timerecords do not match: scalartimeaverage'   # data check
        return trtm, dataAvgOut, flagOut

    def polartimeavg(self, trtm, trD, dirD, spdD, radin=True, interp=True):
        """This function averages polar "data" over the timestep by looking averaging
        data between time steps on a given target output time (trtm).  The funciton uses
        scipy.interpolate.interp1d with extrapolation

        Args:
          trtm: Time record to match): a list of datetime formatted timestamps to match
                data for
          trD: time record data): the timestamp of the input data to be averaged/accounted for
          dirD: theta (angle) variable (ex: wind avgDir)
          spdD: radial value (ex: wind speed)
          radin (bool): will convert if marked false (Default value = True)
          interp (bool): will interpolate across data gaps, if at the beginning/end of record, will just repeat.

        Returns:
            trOut: (time record out) record, in datetime format, of the output record
            avgSpeed: polar averaged speed
            avgDir: polar averaged direction

        NOTE:
            data returned in same rad/deg as input

        """
        from scipy import interpolate
        assert isinstance(trD[0], float) == isinstance(trtm[0], float), 'time data types must be the same (for comparison)'
        flagLoc = np.zeros(np.size(trtm))  # alloccating for x avgDir
        if np.size(trtm) == 1 and type(trtm) is not list and type(trtm) is not np.ndarray:
            trtm = [trtm]
        if radin == 0:
            dirD = np.deg2rad(dirD)  # converting degree to rad

        x, y = anglesLib.pol2cart(spdD, dirD)  # converting from polar to cartesian vectors

        assert len(dirD) == len(trD), 'your data and time records are of different lengths!'  # data check
        for zz in range(0, np.size(trtm)):  # number of records to match
            if zz == np.size(trtm) - 1:  # if its the last record
                if not (trtm[zz] <= trD).any():  # check to make sure its end of record
                    flagLoc[zz] = np.nan # avgList.append(ii)  # take index numbers for values to be averaged
            else:
                if not np.logical_and(trtm[zz] <= trD, trD < trtm[zz + 1]).any():
                    flagLoc[zz] = np.nan #  avgList.append(ii)

        # now find flag
        flagOut = np.isnan(flagLoc)
        #now find nans, interpolate NaN values
        f_x = interpolate.interp1d(trD, x, assume_sorted=True, fill_value=(np.min(x), np.max(x)), bounds_error=False)
        avgX = f_x(trtm)
        f_y = interpolate.interp1d(trD, y, assume_sorted=True, fill_value=(np.min(y), np.max(y)), bounds_error=False)
        avgY = f_y(trtm)

        [avgSpeed, avgDir] = anglesLib.cart2pol(avgX, avgY)  # avgDir in radians

        if radin == False:
            avgDir = np.rad2deg(avgDir)
        # QA/QC plot
        # from matplotlib import pyplot as plt
        # plt.plot(trD, x, 'r.-', label='Data In')
        # plt.plot(trtm, avgX, 'g:.', label='Data out')
        # plt.legend()
        # plt.savefig('QAQC_polartimeaverage.png')
        # plt.close()
        return trtm, avgSpeed, avgDir, flagOut

    def elevationCorrectWind(self, avgspeed, gaugeht):
        """this corrects the wind altitude to MSL at the pier assuming gaugeht is recorded at NAVD88

        Args:
          avgspeed: input array of average wind speed to correct
          gaugeht: the heght of the wind sensor
        
        Returns:
            avgspeed: elevation corrected wind height
        """
        #gaugeht -= 0.128  # NAVD88 to MSL  # no correction needed, everything is in NAVD88 including WL
        if gaugeht <= 20:
            avgspeed *= (10 / gaugeht) ** (1 / 7)
            return avgspeed
        else:
            print('No Corrections done for gauges over 20m, please read: \nJohnson (1999) - Simple Expressions for correcting wind speed data for elevation')
            return avgspeed * 'NaN'

    def geo2grid_spec_rotate(self, dirbin, spec, **kwargs):
        """This function will rotate a spectra to the FRF pier angle
            this will also flip from Clockwise positive to Counter-clockwise positive convention
        
            function finds zero from dirbin (input) and will put that at the begging, it will flip the angle
            convention of the directions (from CW+ to CCW+) then flip the spectra to match

        Args:
          dirbin: direction bins (degrees) to rotate spectra to
          spec: 2D directional Spectra with dimensions [t, freq, Dir]

        Keyword Args:
            'zeroAngle' (float): angle of zero for spectral rotation (Default=70 for FRF pier)

        Returns:
            newdWED: a rotated spectra

            outDirbin: a corrected rotated direction bins associated with the newly rotated directional
                spectra

        """
        zeroAngle = kwargs.get('zeroAngle', 70)
        dirbin = np.array(dirbin) # fixing shape issue
        assert spec.ndim == 3,'spectra must be 3 dimentional [time, freq, dir]'

        rotDirbinTN = anglesLib.geo2STWangle(dirbin, zeroAngle=zeroAngle)  # the energy is placed at the center of these bins

        posmin = np.min(rotDirbinTN)       # a positive value
        negmin = (np.max(rotDirbinTN-360))   # a negative value
        if posmin > np.abs(negmin):
            # does this happen?  should happen using non FRF pier angle
            zero_idx = int(np.argwhere((rotDirbinTN-360) == negmin)) + 1
            # this plus 1 is the cover the non inclusive indexing
            # that is inherant in python
        elif posmin < np.abs(negmin):
            zero_idx = int(np.argwhere(rotDirbinTN == posmin)) + 1
            # this plus 1 is the cover the non inclusive indexing
            # that is inherant in python
        else:
            zero_idx = None
        botdWED = (spec[:, :, 0:zero_idx])
        topdWED = (spec[:, :, zero_idx:])
        # then flipping the angle convention from cw+ to CCW+
        revbotdWED = botdWED[:, :, ::-1]
        revtopdWED = topdWED[:, :, ::-1]
        # now concatenate the flipped and rotated spectra
        newdWED = np.concatenate((revbotdWED, revtopdWED), axis=2)
        # making output degrees in STWAVE, cartesian coords
        outDirbin = np.arange(0, 360, np.median(np.diff(dirbin)))

        return newdWED, outDirbin

    def grid2geo_spec_rotate(self, dirbin, spec):
        """rotate the spetcra from grid space to geographic cordinate conventions
            This will find the zero (or closest) value in dirbin (input) then flip the convention from
            counter-clockwise positive to clockwise positive. then it will flip (rotate) the spectra to patch

        Args:
          dirbin: direction bins by which to rotate the spectra to
          spec: spectra to be rotated [time, freq, dir] assumption
        
        Returns:
            outdWED: a spectra that is rotates to true north with new true north direction bins

            outdirbin: output directions rotated to the spectral output
        """
        spec = np.array(spec)
        assert spec.ndim == 3, 'spectra must be 3 dimentional [time, freq, dir]'
        dirbin = np.array(dirbin)  # fisxing shape issue
        rotDirbinTN = anglesLib.STWangle2geo(dirbin, pierang=70)
        posmin = np.min(rotDirbinTN)       # a positive value
        negmin = (np.max(rotDirbinTN-360))   # a negative value

        if posmin > np.abs(negmin):
            # does this happen?  should happen using non FRF pier angle
            zero_idx = int(np.argwhere((rotDirbinTN - 360) == negmin)) + 1
            # this plus 1 is the cover the non inclusive indexing
            # that is inherant in python
        elif posmin < np.abs(negmin):
            zero_idx = int(np.argwhere(rotDirbinTN == posmin)) + 1
            # this plus 1 is the cover the non inclusive indexing
            # that is inherant in python
        else:
            zero_idx = None
        # finding point to invert (ccw+ to CW+)
        botdWED = (spec[:, :, zero_idx:])
        topdWED = (spec[:, :, 0:zero_idx])
        # then flipping the angle convention from CCW+ to CW+
        revbotdWED = botdWED[:, :, ::-1]
        revtopdWED = topdWED[:, :, ::-1]


        if spec.shape[2] == 35:
#            idx = int(np.argwhere(dirbin == np.min(np.abs(dirbin))))
#            NorthSide = newdWED[:, :, idx:]
#            SouthSide = newdWED[:, :, :idx]
            filler = np.ones((spec.shape[0], spec.shape[1], 72-35)) * 1e-6
#            outDwed = np.concatenate(( SouthSide, filler, NorthSide), axis=2)
            outDwed = np.concatenate((revtopdWED, filler, revbotdWED), axis=2)

        else:
            outDwed = np.concatenate((revtopdWED, revbotdWED), axis=2)

        outDirbin = np.arange(0, 360, np.median(np.diff(dirbin)))

        return outDwed, outDirbin

    def HPchop_spec(self, spec, dirbin, angadj=0, corrected=True):
        """This function chops a spectra into half plane, assuming already shore normal waves,
        it will remove half of the spectra not incident to shore
        
        NOTE: THIS FUNCTION DOES NOT FLIP THE ANGLE CONVENTION FROM CARTESIAN TO GEOGRAPHIC
        USE GEO2GRID SPEC ROTATE FOR THIS
        
          ASSUMPTIONS:
            waves are already shore normal
            follows MET convention (angles measured in the from direction)

        Args:
          spec: 2D directional spectra (record count x frq x direction )
          dirbin: associated directions with the spectra
          angadj: rotation angle to make 0 shorenormal angle in deg true north of shore perpendicular
                MET convention (shore->sea)THE PORTION OF THE SPECTRA traveling opposite this
                will be removed (Default value = 0)
          corrected (bool):  corrected = True for input being between 0:360
                            corrected = False for input containing negative values
                            (Default value = True)
        
        Returns:
            newspec:    new Half plane spectra

            newdirband: direction bands associated with Halfplane spectra

        Notes:
            if angadj ==0 directions are output as Shore Normal
            if angadj !=0 directions are output as True North

        """
        import warnings
        warnings.warn('please use the function in testbedUtils.waveLib.py module')
        dirbin = np.array(dirbin)
        # if angadj != 0:
        #     dirbin = angle_correct(dirbin - angadj)
        if angadj < 0:  # if a
            #rotating dirbin if need be
            dirbin = anglesLib.angle_correct(dirbin - angadj)

        elif angadj > 0:
            dirbin = dirbin - angadj

        zeroidx = abs(np.array(dirbin)).argmin() # index of zero degrees
        deltadeg = np.abs(np.median(np.diff(dirbin)))
        ## number of bins on either side of zero non inclusive of zero (only in HP)
        nbins = int(((360 / 4) - 1) / deltadeg)

        if zeroidx + nbins > len(dirbin):  # if the zero + nbins wraps
            mmidx = zeroidx + nbins - len(dirbin)  # how many wrapped (extra)
            mlist = np.concatenate((list(range(zeroidx, len(dirbin))), list(range(0, mmidx + 1))))
        else:
            mlist = list(range(zeroidx, zeroidx + nbins + 1))  # indicies of new zero to the max on this side of zero
        if zeroidx == 0:
            zzidx = abs(zeroidx - nbins)  # how many wrap
            zlist = list(range(np.size(dirbin) - zzidx, np.size(dirbin)))
        elif zeroidx - nbins < 0:  # if the lower bound of the hp wraps
            zzidx = abs(zeroidx - nbins)  # extra (wrap points)
            zlist = np.concatenate((list(range(np.size(dirbin) - zzidx, np.size(dirbin))), list(range(0, zeroidx))))
        else:
            zlist = list(range(zeroidx - nbins, zeroidx))
        # create newly halfed direction bands and new spectra
        newdirband = np.concatenate([dirbin[zlist], dirbin[mlist]], axis=0)  # pulling proper angle bins together (with shore perp centered
        #newspec = np.zeros([np.size(spec, axis=0), np.size(spec, axis=1), np.size(newdirband)])  # initializing
        newspec = np.concatenate([spec[:, :, zlist], spec[:, :, mlist]], axis=2)  # pulling proper spec data

        if angadj != 0 and corrected == 1:
            newdirband = anglesLib.angle_correct(newdirband + angadj)
        elif corrected == 1:
            newdirband = anglesLib.angle_correct(newdirband)

        return newspec, newdirband

    def prep_spec_phaseResolved(self, rawspec, version_prefix, **kwargs):
        """This function is to generate input for preprocessing stuff for spectral input on swash.
        
        1. upsample spectra (double freq bins)
        2. set cycles/run durations
        
        Keyword Args:
            "spinUpTime" : time in seconds to run the model before outputing data
            "runDuration" : duration to run the model (total) in seconds
            "shoreNormalAngle": used for migrating a 2D spectra to a 1Dspectra (HP truncation)
            "model":  model name (Default=None)
            "nf": frequency count to interpolate spectra to (default=100)
            "phases": will assign phases
            
        """
        assert 'time' in rawspec, "\n++++\nThere's No Wave data to prep \n++++\n"
        nf = kwargs.get('nf', None)  # number of frequencies
        spinUpTime = kwargs.get('spinUpTime', 6*60)
        RunDuration = kwargs.get('runDuration', 30*60)
        model = kwargs.get('model', None)
        angle = kwargs.get('shoreNormalAngle', 71.8)
        phases = kwargs.get('phases', None)
        print('TODO:  Double Check wave directions associated with bathy, frequency banding with TS gen ['
              'prepdataLib.prep_spec_phaseResolved]')
        waveTimeList = kwargs.get('waveTimeList', None)  # default to use all

        # reduce to single spectra
        rawspec = sb.reduceDict(rawspec, np.argwhere(np.in1d(rawspec['time'], [waveTimeList])).squeeze())
        assert rawspec is not None, 'The input data does not match waveTimeList, cannot continue'
        
        # has to be after the dictionary reduction above
        fspec = rawspec['fspec']
        freqbins = rawspec['wavefreqbin']
        if version_prefix.lower() == 'base':

            maxFreq = np.ma.max(freqbins[~fspec.mask])
            minFreq = np.ma.min(freqbins[~fspec.mask])
            df = 1 / RunDuration #Tcycle                       # length of cycle to be compute time
            if nf is None:
                nf = int((maxFreq - minFreq) / df)
            fOut = np.linspace(minFreq, maxFreq, nf)
            #assert rawspec['time'].shape[
            #           0] == 1, "you've pulled too much wave data, are you running longer than 1 hours sims?"
            fSpecOut = np.interp(fOut, freqbins, fspec.squeeze())

            rawspec['fspec'] = fSpecOut
            rawspec['freqbins'] = fOut
            rawspec['runDuration'] = RunDuration
            rawspec['spinUp'] = spinUpTime
            return rawspec

        elif version_prefix.lower() in ['freq'] and model.lower() == 'funwave':
            ## assign variables
            # spec_dates = rawspec['time']
            wavedirbin = rawspec['wavedirbin']  # complete dir vector [deg]

            # waveDp = rawspec['waveDp'] # peak period [sec]
            dWED = rawspec['dWED']  # wave energy density matrix with [freq,dir] dimensions

            [peakf, peakd] = np.unravel_index(dWED.argmax(), dWED.shape) # indeces of peak frequency and peak direction
            peak_dir = wavedirbin[peakd] # peak direction [deg]
            peakF = rawspec['peakf']  # peak frequency [Hz]

            

            [NumFreq, NumDir] = np.shape(dWED)  # number of freq and dir points
            NumFreq = NumFreq - 1  # number of freq segments/bins
            NumDir = NumDir - 1  # number of dir segments/bins

            ## compute the original resolution of freq and dir vectors
            dfreq = (freqbins[-1] - freqbins[0]) / (NumFreq)  # delta freq  --> gaby can you use np.median(np.diff(
                                                                                                            # freqbins)
            ddire = (wavedirbin[-1] - wavedirbin[0]) / (NumDir)  # delta dir

            ## compute directional spectra and frequency spectra respectively
            dWED_Dir = np.sum(dWED, 0) * dfreq  ## where axis 0 = sum of each column (COL = DIR)

            dWED_Frq = np.sum(dWED, 1) * ddire  ## where axis 1 = sum of each row (ROW = FREQ)

            ## Adjust Wave Direction to FUNWAVE format (cartesian)

            angle_cone = 70  # 75

            mod = angle % ddire
            if mod >= ddire / 2:  # adjust rotation angle to the closest angle available in the bins
                offset = np.ceil(angle - mod + ddire)
            else:
                offset = np.floor(angle - mod)

            # angle with respect to funwave (0 deg is cros-shore, [-] toward south, and [+] toward north)
            main_dir = ((angle_cone - offset) - (angle_cone - peak_dir))

            d_range = [main_dir - angle_cone, main_dir + angle_cone]  # funwave angle cone
            Dire_model = np.arange(d_range[0], d_range[1] + ddire, ddire)  # new truncated direction vector in FF

            d_range_TN = [peak_dir - angle_cone, peak_dir + angle_cone]  # TN angle cone
            Dire_TN = np.arange(d_range_TN[0], d_range_TN[1] + ddire, ddire)  # new direction vector in TN

            # DIRE = np.zeros(np.shape(Dire_TN))  # same as Dire_TN, but without the negative values
            # for i, angles in enumerate(Dire_TN):
            #     if angles < 0:
            #         DIRE[i] = 360 + angles
            #     else:
            #         DIRE[i] = angles
            DIRE = anglesLib.angle_correct(Dire_TN) # ----> gaby this function will correct angles if  they're
                                                            # above/below 0/360

            ## Define the number of Freq and Dir points of truncated vectors (with original resolution)
            f_range = [0.04, 0.3775]                                    # desired freq range (Hz)
            Freq = np.arange(f_range[0], f_range[1] + dfreq, dfreq)     # desired freq vector

            MaxFreqNum = len(Freq)           # max number of desired Frq points (should be 46 for FRF case)
            MaxDireNum = len(DIRE)           # max number of desired Dir points (should be 31 for FRF case)


            NFreq = min(NumFreq, MaxFreqNum)  # select min value between available and desired number of Freq bins
            NDir = min(NumDir, MaxDireNum)  # select min value between available and desired number of Dir bins

            ## Truncate energy density matrix
            #n_peakf = np.arange(max(0, peakf - np.floor(NFreq / 2) - 1),
            #                    min(NumFreq, peakf + np.floor(NFreq / 2)) + 1)  # truncated freq index range

            n_peakf = np.arange(np.where(Freq==0.04)[0][0],np.where(Freq>=0.30)[0][0]) # truncated freq index to fixed [0.04, 0.3] Hz range
            n_peakd = np.zeros(MaxDireNum)  # truncated dir index range

            for j in range(MaxDireNum):
                for k, angle in enumerate(wavedirbin):
                    if angle == DIRE[j]:
                        n_peakd[j] = int(k) - len(wavedirbin)

            Freq_model = Freq[n_peakf.astype(int)]  # extract the freq on the truncated index ranges
            dWED_model = dWED[n_peakf[0].astype(int):n_peakf[-1].astype(int) + 1,
                         n_peakd.astype(int)]  # extract the dWED on the truncated index ranges

            dWED_Dir_model = np.sum(dWED_model, 0) * dfreq  # truncated directional spectra
            dWED_Frq_model = np.sum(dWED_model, 1) * ddire  # truncated frequency spectra


            ## Compute total energy density, Hrms & Hsig (from complete spectra)
            totalE_complete = np.sum(dWED * dfreq * ddire)
            Hrms_complete = np.sqrt(totalE_complete * 8)
            Hsig_complete = np.sqrt(2) * Hrms_complete

            print('For complete spectra ===> totalE = ',
                  str(totalE_complete), 'J/(m^3), Hrms = ', str(Hrms_complete), 'm'
                                            ', & Hsig = ', str(Hsig_complete),'m\n')

            ## Compute model energy density, Hrms & Hsig (from truncated spectra)
            totalE_model = np.sum(dWED_model * dfreq * ddire)
            Hrms_model = np.sqrt(totalE_model * 8)
            Hsig_model = np.sqrt(2) * Hrms_model

            print('For truncated spectra ===> totalE = ',
                  str(totalE_model), 'J/(m^3), Hrms = ', str(Hrms_model), 'm'
                                        ', & Hsig = ', str(Hsig_model), 'm\n')

            ## Compare truncated values to the total values
            TotalE_error = abs((totalE_model - totalE_complete) / totalE_complete) * 100
            Hrms_error = abs((Hrms_model - Hrms_complete) / Hrms_complete) * 100
            Hsig_error = abs((Hsig_model - Hsig_complete) / Hsig_complete) * 100

            print('TotalE_%error = ', TotalE_error,
                  '% \nHrms_%error =  ', Hrms_error,
                  '% \nHsig_%error =  ', Hsig_error, '%')

            ## Change dfreq to new resolution
            print("\nInterpolating spectra based on %d number of frequency bins."%(int(nf)))
            new_ddire = ddire # delta dire stays the same (for now)
            rotDirbin = np.arange(Dire_model[0], Dire_model[-1] + new_ddire, new_ddire)

            interpFrqbin = np.linspace(Freq_model[0], Freq_model[-1], nf)
            new_dfreq = (interpFrqbin[1]-interpFrqbin[0])#/(nf) # new delta freq

            print('Old dfreq = %.5f' % (dfreq), '-->  New dfreq  = %.7f' % (new_dfreq))
            print('Old NumFreq =', len(Freq_model), '-->  New NumFreq =', len(interpFrqbin))


            ## Interpolate spectra to new frequency resolution
            interp_matrix = interpolate.interp2d(Dire_model, Freq_model, dWED_model)
            interp_dWED = interp_matrix(rotDirbin,interpFrqbin)
            [new_NumFreq,new_NumDir] = np.shape(interp_dWED)

            ## Compute Total Energy, Hrms and Hmo of interpolated spectra
            totalE_interp = np.sum(interp_dWED * new_dfreq * new_ddire)
            Hrms_interp = np.sqrt(totalE_interp * 8)
            Hsig_interp = np.sqrt(2) * Hrms_interp

            print('\nFor truncated spectra with original dfreq ===> totalE = ',
                  str(totalE_model), 'J/(m^3), Hrms = ', str(Hrms_model), 'm'
                  ', & Hsig = ', str(Hsig_model), 'm\n')

            print('For interpolated spectra with new dfreq ===> totalE = ',
                  str(totalE_interp), 'J/(m^3), Hrms = ', str(Hrms_interp), 'm'
                  ', & Hsig = ', str(Hsig_interp), 'm\n')

            TotalE_error_interp = abs((totalE_model - totalE_interp) / totalE_model) * 100
            Hrms_error_interp = abs((Hrms_model - Hrms_interp) / Hrms_model) * 100
            Hsig_error_interp = abs((Hsig_model - Hsig_interp) / Hsig_model) * 100

            print('TotalE_%error = ', TotalE_error_interp,
                  '% \nHrms_%error =  ', Hrms_error_interp,
                  '% \nHsig_%error =  ', Hsig_error_interp, '%')

            ## compute 2d amplitude
            amp2d = (np.sqrt(interp_dWED * new_dfreq * new_ddire*8.0)/2.0).T

            ## compute 1d amplitude
            dWED_Dir_interp = np.sum(interp_dWED, 0) * new_dfreq  # interpolated directional spectra
            dWED_Frq_interp = np.sum(interp_dWED, 1) * new_ddire  # interpolated frequency spectra

            amp1d = np.sqrt(dWED_Frq_interp*new_dfreq*8.0)/2.0

            ## now package into dictionary (use same keys as above)

            wavepacket = {
                'name': rawspec['name'],
                'spec2d': interp_dWED,
                'amp1d':amp1d,
                'amp2d':amp2d,
                'wavedirbin': rotDirbin,
                'wavefreqbin': interpFrqbin,
                'peakf': rawspec['peakf'],
                'waveDp': rawspec['waveDp'],
                'time': rawspec['time'],
                'phases': phases,
                'Hs': Hsig_interp,
                'waveDm': rawspec['waveDm']
                }


            return wavepacket

            #now interpolatate 2D spectra frequency spectra
            # truncate and integrate 2D spectra to 1D
            #       use angle variable from above, use nf from above
    
            # add conversion from m2 - > m for funwave spectral input (i think you've done this)
            
            # interpolate 1D spectra to new nf values
            
            # load phase info from grids/FUNWAVE/phases.pickle
            
            
            #now package into dictionary (use same keys as above)
            # frequency's
            # fspec
            # -- don't need direction
            # do we need spin up time or runDuration (is this going to change) i don't think so?? but think about it
            #   this get's put into write spectra function
            return None
            
            

    def prep_spec(self, rawspec, version_prefix, datestr, plot=False, full=False, deltaangle=5, outputPath='', **kwargs):
        """directional spectra come into this function and are half planned and rotated to shore normal
            a phase averaged spectra rotation and interpolation scheme with QA/QC plotting capability
            spectral linear interpolation as well

        Args:
          rawspec: a dictionary from get data with keys
             'wavedirbin': direction bins associated with dWED

             'dWED': directional wave energy density (2 d spectra) shape assumption [t, freq, dir]

             'wavefreqbin:  direction bins associated with dWED

             'name': gauge name

             'peakf': peak frequency

             'time': times associated with t in dwed (should be date time)

          version_prefix (str): string - a key associated with various switches to process data differntly
                example 'HP' half plane --- removes have of the spectral energy (non-incident)

          datestr (str): a date string associated with the simulation run time format: yyyymmddTHHMMSSZ

          plot (bool): true or false (Defalut value = 0 /False) (Default value = 0)

          full (bool): describes full or half plane, requires spectral truncation for HP (Default value = False)

          deltaangle (int): the directional bin size for output (Default value = 5)

          outputPath (str): the full path for output plotting files -- assumes there is a figures folder in place (
                Default value = '')

          **kwargs:
            'CMSinterp' (bool): will interpolate spectra to max of 50 frequency bins
            'model' (str): important for CMS or ww3 or will assume STWAVE
            'ww3nFreq' (int): number of frequency bins  for ww3 (default = 35)
            'waveTimeList'(list): list of times to match, (Default = use all times from rawspect)

        Returns:

        """
        assert rawspec is not None, "\n++++\nThere's No Wave data \n++++\n"
        model = kwargs.get('model', 'stwave')
        ww3nfreq = kwargs.get('ww3nFreq', 35)
        cmsInterp = kwargs.get('CMSinterp', None)  # default to use all
        waveTimeList = kwargs.get('waveTimeList', None) # default to use all
        ################################################################################################################
        ################################################################################################################
        if waveTimeList is not None:  # reduce wave dictionary if needed
            rawspec = sb.reduceDict(rawspec, np.argwhere(np.in1d(rawspec['time'], list(waveTimeList))).squeeze())
            assert rawspec is not None, 'The input data does not match waveTimeList, cannot continue'
        if 'time' in rawspec:
            # converting loaded energy density from 'm2 s /deg' to 'm2/hz/rad'
            # this is required for input into the model
            rawspec['dWED'] = np.rad2deg(rawspec['dWED'])
            # this is inverse of deg2rad because deg is on the bottom
            # __________________________________________________________________
            # rotation of angle convention for  input spectra
            if model is None or model.lower() in ['stwave', 'cms-wave', 'cms']:
                # flip direction convention from  + CC to +CCW and create new zero
                [rot_dWED, rotDirbin] = self.geo2grid_spec_rotate(rawspec['wavedirbin'], rawspec['dWED'], zeroAngle= 72)
            elif model.lower() in ['ww3']:
                # convert directions to oceanographic and flip directions
                rotDirbinTemp = anglesLib.angle_correct(rawspec['wavedirbin']-180)[::-1]
                arg90 = np.argwhere(rotDirbinTemp == 90).squeeze()  # find 90 to shift

                ## flip orientation so input is 90 -> 0 -> 355 -> 85
                argsSort = np.concatenate([np.arange(arg90, len(rotDirbinTemp)), np.arange(0, arg90)])
                rawspec['wavedirbin'] = rotDirbinTemp[argsSort]   # over write direction bins for interpolation
                rot_dWED = rawspec['dWED'][:, :, argsSort]        # sort spectra to match that of directions
                # #
                # from matplotlib import pyplot as plt
                # from matplotlib import colors
                # plt.figure(); tidx=100; plt.suptitle('prepData: interp IN')
                # plt.subplot(121)
                # plt.pcolormesh(rot_dWED[tidx], norm=colors.LogNorm()); plt.colorbar();
                # plt.subplot(122)
                # plt.pcolormesh(rawspec['wavedirbin'], rawspec['wavefreqbin'], rot_dWED[tidx,:, :], norm=colors.LogNorm());
                # plt.colorbar(); plt.text(200, 0.25, '$E_T$ - {:.2f}'.format(np.deg2rad(rot_dWED[tidx]).sum()))
            # _________________________________________________________________
            # initializing for interpolation
            if np.median(np.diff(rawspec['wavedirbin'])) != deltaangle or 'CMSinterp' in kwargs or model.lower() in ['cms', 'ww3']:
                if cmsInterp is not None: # then interpolate in frequency
                    newwavedirbin = np.arange(0, 360, deltaangle)  # creating a direction bin for interpolation over
                    # interpolating the spectra in frequency
                    nfrqbin = kwargs['CMSinterp']  # 50 should be max as described by the model
                    interpFrqbin = np.linspace(rawspec['wavefreqbin'][0], rawspec['wavefreqbin'][-1], nfrqbin)
                    fillvalue= 1e-6
                elif model.lower() in ['ww3']:
                    ## create newFreq banding at 1.1 * previous cell, lower bound at 26.3 seconds
                    newFreq, bw, low, high = [0.038], [0.38 / 2], [0], []
                    for ii in range(1, ww3nfreq):
                        newFreq.append(newFreq[ii - 1] * 1.1)
                        low.append(newFreq[ii - 1] + (newFreq[ii] - newFreq[ii - 1]) / 2.0)
                        high.append(newFreq[ii] - (newFreq[ii] - newFreq[ii - 1]) / 2.0)
                        bw.append(newFreq[ii] - newFreq[ii - 1])  # band width
                    high.append(np.ceil(newFreq[-1]))             # high bound of frq bin
                    interpFrqbin = np.array(newFreq)              # band center freq bin
                    newwavedirbin = rawspec['wavedirbin']           # interpolate to same direction, we already sorted above
                    fillvalue = None
                else:
                    newwavedirbin = rawspec['wavedirbin']           # interpolate to same direction, we already sorted above
                    interpFrqbin = rawspec['wavefreqbin']
                    fillvalue = 1e-6
                ########### Begin interpolation in frequency and direction as decided above (based on model) ###########
                # allocating the interpolating equation array
                interp_dWED = np.zeros([np.size(rot_dWED, axis=0), np.size(interpFrqbin, axis=0), np.size(newwavedirbin, axis=0)])
                for tt in range(0, np.size(rot_dWED, axis=0)):
                    f = interpolate.interp2d(rawspec['wavedirbin'], rawspec['wavefreqbin'],
                                         rot_dWED[tt, :, :], fill_value=fillvalue,  kind='linear')
                    interp_dWED[tt, :, :] = f(newwavedirbin, interpFrqbin)
                    # interp_dWED[dir_ocean, :, :] = interp_dWED[dir_ocean, :, :]  # interpolating over the new direction bin
                rotDirbin = newwavedirbin

            else:  # no interpolation needed
                interp_dWED = rot_dWED # no interp needed
                interpFrqbin = rawspec['wavefreqbin']

            # ________________________________________________________________
            # write packet
            if full == False:  # full plane off
                # the angles going into HPchop are associated the cartesian grid at this point
                # therefore they do not need to be 'rotated' in HPchop
                from testbedutils import waveLib
                [interp_dWED, _] = waveLib.HPchop_spec(interp_dWED, rotDirbin, angadj=0)
                # this resets the output, only used to pass on proper number of dirbins
                rotDirbin = np.arange(-85, 90, 5)

            wavepacket = {'name': rawspec['name'], 'spec2d': interp_dWED, 'wavedirbin': rotDirbin,
                          'wavefreqbin': interpFrqbin, 'peakf': rawspec['peakf'], 'time': rawspec['time']}
            if model in ['ww3']:
                wavepacket['lon'], wavepacket['lat'] = rawspec['lon'], rawspec['lat']
                wavepacket['xFRF'], wavepacket['yFRF'] = rawspec['xFRF'], rawspec['yFRF']

            #____________________mark data for interpolation in time and flag ___________________________________
            # # running through each snap record create file bases for timestamping data
            flag = 0
            if np.size(rawspec['time']) > 1:
                wavetime, dt = [], []  # datetime version of time
                for dd in range(0, np.size(rawspec['dWED'], axis=0)):
                    wavetime.append((rawspec['time'][dd]))
                dtlist = np.diff(wavetime)
                for nn in range(0, len(dtlist) - 1):
                    dt.append(dtlist[nn].seconds)
                dt = np.median(dt)  # reading the mean delta time by taking median of all records in file
                for ee in range(0, len(dtlist)):
                    if dtlist[ee].seconds != dt:  # if the ind delta record is different than the median of the file
                        flag = 1
            if flag == 0:
                wavepacket['flag'] = np.zeros(np.size(rawspec['time']))#len(wavetime))
            elif flag == 1:
                import pdb
                pdb.set_trace()
                ttemp = nc.date2num(wavepacket['time'],'seconds since 1970-1-1')
                # run through time interpolation ( filling missing records, mark those that are filled)
                [wavepacket['spec2d'], aflag] = self.insertfun(wavepacket['spec2d'], dtlist)
                wavepacket['spec2d'] = self.wlinterp(wavepacket['spec2d'], aflag)
                [wavepacket['time'], bflag] = self.insertfun(ttemp, nc.date2num(dtlist,'seconds since 1970-1-1'))
                wavepacket['time'] = self.wlinterp(ttemp, bflag)  # interpwavetime
                [wavepacket['peakf'], cflag] = self.insertfun(wavepacket['peakf'], dtlist)
                wavepacket['peakf'] = self.wlinterp(wavepacket['peakf'], cflag)
                assert (aflag == bflag).all(), "flag records don't match between directional spectra and timestamp"
                wavepacket['flag'] = aflag

            if np.size(wavepacket['time']) >= 1:
                wavepacket['snapbase'] = [(t.strftime('%Y%m%d%H%M')) for t in wavepacket['time']]
                wavepacket['epochtime'] = [(t - DT.datetime(1970, 1, 1)).total_seconds() for t in wavepacket['time']]

            # _________________________________________________________________
            # plotting
            if plot is True:
                # plot a tripple comparison of the input spectra for quality checking
                from plotting.operationalPlots import plotTripleSpectra
                for tt in range(rawspec['dWED'].shape[0]):
                    if full == 0:
                        plotnewwavedirbin = list(range(-85, 90, 5))
                        interpDwed = interp_dWED[tt, :, :]
                    elif full == 1:
                        plotnewwavedirbin = list(range(-180, 180, 5))
                        interpDwed= np.concatenate((interp_dWED[tt, :, 36:], interp_dWED[tt, :, :36]),
                                                   axis=1)
                    raw = (rawspec['dWED'][tt, :, :], rawspec['wavedirbin'], rawspec['wavefreqbin'])
                    rot = (rot_dWED[tt, :, :], list(range(0, 360, 5)), rawspec['wavefreqbin'])
                    interp = (interpDwed, plotnewwavedirbin, interpFrqbin)
                    Hs = (rawspec['Hs'][tt], rawspec['time'],  rawspec['Hs'][:])
                    fName = os.path.join(outputPath, 'figures/CMTB_{}_inputspec_{}.png'.format(version_prefix,
                                                                                            wavepacket['snapbase'][tt]))
                    time = rawspec['time'][tt]
                    plotTripleSpectra(fName, time, Hs, raw, rot, interp)

                fList = sorted(glob.glob(os.path.join(outputPath, 'figures/CMTB_{}_inputspec_*.png'.format(
                    version_prefix))))
                moveFname = os.path.join(outputPath, 'figures/CMTB_{}_inputspec_{}.mp4'.format(
                    version_prefix, datestr))
                sb.makeMovie(moveFname, fList)
                sb.myTarMaker(os.path.join(outputPath,  'figures', 'CMTB_spec.tar.gz'), fList, removeFiles=True)
            print("number of wave records {} with {} interpolated points".format(np.shape(wavepacket['spec2d'])[0],
                                                                                 wavepacket['flag'].sum()))

            return wavepacket
        else:
            print('There is no wave data!!! cannot prep')
            return None

    def prep_Bathy(self, bathy, gridNodes, positiveDown=True, **kwargs):
        """This function takes in a new bathy (from integrated bathy product) and interpolates and truncates
         the grid to match the model domain in gridNodes, with convert to positive down
        it preps the dictionary for write dep function from input output.  Function can handle both rectilinear
        grid or unstructured grid (need unstructured=True in kwargs)

        Args:
          bathy: must be a dictionary with the following keys contains bathy from integrated bathy product
            'elevation':  bathy elevation

            'xFRF': x coords of nodes in FRF coords

            'yFRF':  y coords of grid nodes in FRF

          gridNodes(dict): information about grid nodes, below structure if rectilinear grid, if not, assume
                    assume meshio type structure of gridNodes.points having the lat/lon values in 1,0 respectively
             'xFRF': FRF local coordinate system - cross shore location

             'yFRF': FRF local coordinate system - alongshore location

             'northing': NC stateplane - northing

             'easting':  NC stateplane - easting

             'longitude': longitude

             'latitude': latitude

          positiveDown (bool): Function will check to make sure most of the data are positive (or negative if false
                is selected) (Default value = True)

        Keyword Args:
            'unstructured'(bool): will do a linear unstructured interpolation (triangular) if true (default =False)
            'plotFname' (bool): will create a QA/QC plot if a fileName is given
            'gridName' (str): this is meta data written to the file about the grid (Default value ='CMTB_DEFAULT_GRID')
                             if False, it will not plot.  donot use None

        Returns:
          dictionary with keys ready for file write function
            'data': interpolated/prepared bathymetry

            'DataDims: dictionary with keys

            'DataType': filled with 0

            'NumRecs': number of bathy's (assumed 1)

            'NumFlds': number of fields (assumed 1)

            'NI': number of cells in I

            'NJ': number of cells in j

            'DX': cell spacing in x

            'DY': cell spacing in y

            'AZIMUTH': grid rotation

            'GridName': a name for the grid, a good way to pass meta-data!

            'Dataset': dictionary with keys

            'FldName(1)': filled with 'Depth'

            'FldUnits(1)': filled with blank string

            'xFRF': x coords of nodes in FRF coords

            'yFRF': y coords of grid nodes in FRF

            'easting': NC stateplane - easting

            'northing': NC stateplane - northing

            'lon':longitude

            'lat': latitude

        """
        unstructured = kwargs.get('unstructured', False)
        gridName = kwargs.get('gridName', 'CMTB_DEFAULT_GRID')
        plotFname = kwargs.get('plotFname', False)
        
        ### chose which interpolation scheme and implement
        if unstructured:
            from matplotlib import tri
            if isinstance(gridNodes, dict):
                gridNodes = sb.Bunch(gridNodes)
            
            triObj = tri.Triangulation(bathy['lon'].flatten(), bathy['lat'].flatten()) # making the triangles
            ftri = tri.LinearTriInterpolator(triObj, bathy['elevation'].flatten()) # making the interpolation function
            newZs = ftri(gridNodes.points[:, 0], gridNodes.points[:, 1])    # the actual interpolation
            oldZs = np.copy(gridNodes.points[:, 2])   ## for plotting
            if positiveDown:
                gridNodes.points[~newZs.mask, 2] = -newZs[~newZs.mask]  # replacing values in total data structure
            else:
                gridNodes.points[~newZs.mask, 2] = newZs[~newZs.mask]  # replacing values in total data structure

        else: # assume rectilinear grid
        # this interpolation scheme assumes orientation to on east coast with increasing coordinates to the north (frf system)
            f = interpolate.interp2d(sorted(bathy['xFRF']), sorted(bathy['yFRF']), bathy['elevation'], kind='linear')  # different interp method
            bathyOut = f(gridNodes['xFRF'][:], gridNodes['yFRF'][:])[::-1, :]  # flipped

            ### correct for bathymetry positive up or down
            if positiveDown: # assume that more points in dep file are 'below water'
                if np.median(bathyOut) < 0:
                    bathyOut = -bathyOut # flip sign if data are mostly negative and positive is assumed down
            elif positiveDown == False:
                if np.median(bathyOut) > 0:
                    bathyOut = -bathyOut  # flip sign if data are mostly positive and negitive is assumed down

        ### plot QA/QC plot if necessary
        if plotFname is not False and unstructured:
            from matplotlib import pyplot as plt
            plt.figure()
            ax1 = plt.subplot(211)
            ax1.tripcolor(gridNodes.points[:, 0], gridNodes.points[:, 1], gridNodes.points[:, 2])

            ax1.triplot(gridNodes.points[:, 0], gridNodes.points[:, 1], 'k.', ms=2)
            ax1.plot([-75.75141733166804, -75.74613556618358], [36.18187930529555, 36.18328286289117], color='black',
                     ms=10)  # [],'k-')
            ax1.text(-75.75141733166804, 36.18187930529555, 'FRF                           ', fontsize=14,
                     horizontalalignment='right')

            ax2 = plt.subplot(212, sharex=ax1, sharey=ax1)
            ax2.set_title('difference plot (old-new)')
            cbar2 = ax2.tripcolor(gridNodes.points[:, 0], gridNodes.points[:, 1], oldZs - gridNodes.points[:, 2], cmap='RdBu')
            plt.colorbar(cbar2)
            ax1.set_ylim([bathy['lat'].min(), bathy['lat'].max()])
            ax1.set_xlim([bathy['lon'].min(), bathy['lon'].max()])
            plt.savefig(plotFname); plt.close()
        if unstructured:
            return gridNodes

        else:
            # bathy data needs to be flipped in the cross shore (origin is offshore)
            # and alongshore, data need to be written from opposite origin ato location
            bathyOut = bathyOut[::-1, ::-1]  # data are in [nj, ni] shape
            numrecs =  1  # number of bathys
            numFlds =  1  # number of fields
            fldName = '"Depth"'
            dataDims= {'DataType': 0,
                       'NumRecs': numrecs,
                       'NumFlds': numFlds,
                       'NI': gridNodes['NI'],
                       'NJ': gridNodes['NJ'],
                       'DX': gridNodes['DX'],
                       'DY': gridNodes['DY'],
                       'AZIMUTH': gridNodes['azimuth'],
                       'GridName': '"' + gridName + '"',}
            dataset = {'FldName(1)': fldName, 'FldUnits(1)': '""'}
            out = {'data': bathyOut,
                   'DataDims': dataDims,
                   'Dataset': dataset,
                   'xFRF': gridNodes['xFRF'],
                   'yFRF': gridNodes['yFRF'],
                   'easting': gridNodes['easting'],
                   'northing': gridNodes['northing'],
                   'lon': gridNodes['longitude'],
                   'lat': gridNodes['latitude']}
            return out

    def prep_CMSbathy(self, newBathy, simfile, backgroundGrid):

        """This function takes background sim file and dep file and will ingest these files to create georectified
        cell centered positions with

        Args:
          newBathy (dict): contains bathy to integrate to background
            'xFRF' frf x coordinate

            'yFRF' frf y coordinate

          simfile: file name input for simulation sim
          backgroundGrid: input grid

        Returns: dictionary with keys:
            'xCoord': frf x coordinate

            'yCoord': frf y coordinate

            'elevation': 3 dimensional (t, x, y) bathy ,

            'time': time of grid

            'lat': 2 d latitude ,of cell nodes

            'lon': 2 d longitude,

            'northing': 2 d NC stateplane Northing,

            'easting': 2d NC stateplane Easting

            'x0'(float): grid origin (cell centeric) in FRF x

            'azimuth' (float): grid orienttation

            'y0' (float): gri origin vertex located in NC Stateplane (taken from background file)


        """
        from . import inputOutput

        minX = newBathy['xFRF'].min()
        minY = newBathy['yFRF'].min()
        maxX = newBathy['xFRF'].max()
        maxY = newBathy['yFRF'].max()

        cio = inputOutput.cmsIO()
        sim = cio.ReadCMS_sim(simfile)
        dep_pack = cio.ReadCMS_dep(backgroundGrid)

        backgroundBathy = np.expand_dims(dep_pack['bathy'][:, :].T, axis=0) # dims [x, y] - shore on left, deep right
        background = gridTools.makeCMSgridNodes(float(sim[0]), float(sim[1]),
                                                float(sim[2]), dep_pack['dx'], dep_pack['dy'],
                                                backgroundBathy)

        # remove min max from background here
        xx2, yy2 = np.meshgrid( background['xFRF'], background['yFRF'])
        mask = (yy2 > minY) & (yy2 < maxY) & (xx2 > minX) & (xx2 < maxX)
        maskedBathy = np.ma.array(background['elevation'][0], mask= mask)
        # now remove masks from background data
        removed_x = xx2[~maskedBathy.mask]  # removed masked areas from x coord grid
        removed_y = yy2[~maskedBathy.mask]  # remove masked areas from y coord grid
        removed_z = np.array(maskedBathy[~maskedBathy.mask])  # removed masks from elevations
        # now do the same with the combine background and new data
        # invert integrated bathymetry in x direction (to match that of CMS) --- weird things
        newBathymetry = -np.squeeze(newBathy['elevation'])[:, :] # turn positive down, flip in alongshore direction
        xx, yy = np.meshgrid(newBathy['xFRF'], newBathy['yFRF'][:])
        # sort the values pre interpolate

        combined_x = np.append(removed_x, xx.flatten())
        combined_y = np.append(removed_y, yy.flatten())
        combined_z = np.append(removed_z, newBathymetry.flatten())

        # print '   incorporating integrated bathymetry product into background'
        t = DT.datetime.now()
        # elevation_points2 = mlab.griddata(combined_x, combined_y, combined_z, background['xFRF'], background['yFRF'], 'linear')
        grid_x, grid_y = np.meshgrid(background['xFRF'], background['yFRF'])
        elevation_points = interpolate.griddata((combined_x, combined_y), combined_z, (grid_x, grid_y), method='linear')
        print('   bathy integration took %s' %(DT.datetime.now() - t))

        # Correct bathy out as needed to fit write dep function
        elevation_points = elevation_points[::-1, :] # dims [y, x]
        # now use background node locations for output
        out = {'xFRF': background['xFRF'],
               'yFRF': background['yFRF'],
               'elevation': np.expand_dims(elevation_points.T, axis=0),  # exported as [t, y, x]
               'time': background['time'],
               'lat': background['latitude'],
               'lon': background['longitude'],
               'northing': background['northing'],
               'easting': background['easting'],
               'x0': float(sim[0]),
               'azimuth': float(sim[2]),
               'y0': float(sim[1]),}

        return out

    def prep_SwashBathy(self, x0, y0, bathy, yBounds=[940, 950], **kwargs):
        """Takes in bathy dictionary from get bathy data

        Args:
            x0 (float): cross-shore location of computational grid origin (xFRF location of gauge)
            y0 (float); alongshore location of computational grid origin (yFRF location of gauge)
            bathy (dict): a dictionary with required keys
                'xFRF': x coordinate in FRF

                'yFRF': y coorindate in FRF

                'elevation': bathymetry

            yBounds(list): a list of size two that describes the bounds in the alongshore direction,
                    defaults to cross-shore array (Default=[940, 950])

        Keyword Args:
            'dx'(float): resolution in x (default = 1 m)
            'dy'(float): resolution in y (default = 1 m)

        Returns:
            swsPacket(dict):
                'mx'(int): number of mesh's in xCoord
                'my'(int): number of mesh's in yCoord
                'dx':  mesh/grid resolution [m]
                'dy':  mesh/grid resolution [m]
                'xpc': origin of computational grid in larger coord
                'ypc':  origin of computational grid in larger coord
                'alpc': orientation of grid (degrees counter clockwise rotation
                    from true North), to larger coord (default = 0)

            bathyOut(dict)
                "elevation": interpolated bathymetry
        """
    
        #  mesh/grid resolution [m] set default resolution
        dx = kwargs.get('dx', 1.)
        dy = kwargs.get('dy', 1.)
        alpc = kwargs.get('alpc', 0)              # degrees counter clockwise rotation from true North
        xpc = x0                                  # origin of computational grid in larger coord
        ypc = y0                                  # origin of computational grid in larger coord
    
        mx = np.round(x0)/dx                      # number of mesh outputs
        my = np.squeeze(np.diff(yBounds)/dy)      # number of mesh outputs
        if my < 3: my=3
        ###  now interp bathy to dx,dy
        f = interpolate.interp2d(bathy['xFRF'], bathy['yFRF'], bathy['elevation'])
        newXFRF = np.linspace(0, np.round(x0), int(mx), endpoint=True)
        newYFRF = np.linspace(yBounds[0], yBounds[1], int(my), endpoint=True)
        interpedBathy = f(newXFRF,  newYFRF)
        # bathy corresponding mx = 1 length
        swsPacket = {'mx':   mx,
                     'my':   my,
                     'dx':   dx,
                     'dy':   dy,
                     'xpc':  xpc,
                     'ypc':  ypc,
                     'alpc': alpc,
                     'h': interpedBathy, 'xFRF': newXFRF, 'yFRF': newYFRF}
            
        return swsPacket

    def prep_wind(self, rawwind, timerecord, **kwargs):
        """This is designed to take the raw  wind and pre process to model input.

          winds are rotated to oceanographic
          steps in this function:
            1. polar time averaged
            2. winds are interpolated
            3. winds are flagged as interped
            4. winds are elevation corrected to 10m with simple boundary layer log law function

        Args:
          rawwind:
            'winddir': input wind direction as function of time

            'time': time associated with input wind directions and speeds

            'windspeed': speeds in array with time

          timerecord (list datetime objects): this is a record of datetimes for the wind to match

        Keyword Args:
            'model': can denote 'cmsf' to add extra output for non-rotated winds
                     can denote 'ww3' to put winds in global coordainte with oceanographic
                            direction convention


        Returns:
          dictionary with keys
            'name' (str): gauge name

            'avgspd (float): vector averaged wind speed (interpolated in time)

            'avgdir (float): vector averaged wind direction (interpolated in time)

            'time' (float): time associated with output

            'flag' (float): flags to mark the interpolated values

        will return none if a None type object is put in for rawwind input argument

        """
        model = kwargs.get('model', None)
        try:
            if rawwind is not None:  # if there is no wind
                if 'epochtime' not in list(rawwind.keys()):
                    rawwind['epochtime'] = nc.date2num(rawwind['time'], 'seconds since 1970-01-01')
                try:
                    timerecord = nc.date2num(timerecord, 'seconds since 1970-01-01')
                    if timerecord.dtype == 'int64':
                        temprecord = np.zeros(len(timerecord))
                        for itemp, temp in enumerate(timerecord):
                            temprecord[itemp] = float(temp)
                        timerecord = temprecord
                except TypeError:
                    pass     # already in epoch time
                # rename and remove NaN's or masks
                windDir = rawwind['winddir']
                windTime = rawwind['epochtime']
                windSpeed = rawwind['windspeed']
                # first remove data from all bad wind speeds
                if np.ma.array(windSpeed).mask.any():
                    windDir = windDir[~windSpeed.mask].squeeze()
                    windTime = windTime[~windSpeed.mask].squeeze()
                    windSpeed = windSpeed[~windSpeed.mask].squeeze()
                if np.ma.array(windDir).mask.any():
                    # then remove data from all bad wind Directions
                    windSpeed = windSpeed[~windDir.mask].squeeze()
                    windTime = windTime[~windDir.mask].squeeze()
                    windDir = windDir[~windDir.mask].squeeze()
                # Then assert that the data all match up properly
                assert len(windDir) == len(windTime) == len(windSpeed), 'Wind Speeds and Directions are of different lengths, cannot prep'
                # convert wind direction to STWAVE convention (cartesian space)

                if model == 'ww3':  # operates in global coordinate system instead of local coordinate system
                    [_, avgspeed, avgDir, flagOut] = self.polartimeavg(timerecord, windTime, windDir,
                                                                        windSpeed, radin=False)
                    stdirec = anglesLib.angle_correct(avgDir+180, rad=False)  # correct angles to 0-360
                else:
                    windDirMath = anglesLib.geo2STWangle(windDir)
                    [_, avgspeed, avgDir, flagOut] = self.polartimeavg(timerecord, windTime, windDirMath,
                                                                       windSpeed, radin=False)
                    stdirec = anglesLib.angle_correct(avgDir, rad=False)   # correct angles to 0-360


                avgspeed = self.elevationCorrectWind(avgspeed, rawwind['gaugeht'])
                # ________________________________________________________________
                windpacket = {'name': rawwind['name'],
                              'avgspd': avgspeed,
                              'avgdir': stdirec,
                              'time': [DT.datetime(1970, 1, 1) + DT.timedelta(seconds=t) for t in timerecord],
                              'flag': flagOut}

                if model == 'cmsFlow':
                    # one extra for cms-flow if needed
                    [_, _, stdirec_flow, _] = self.polartimeavg(timerecord, windTime, windDir,
                                                                windSpeed, radin=False)
                    windpacket['avgdir_CMSF'] = anglesLib.angle_correct(stdirec_flow, rad=False)

                print('  -- {} wind records with {} interpolated'.format(np.size(windpacket['time']),
                                                                         sum(windpacket['flag'])))
                return windpacket

        except (RuntimeError, TypeError):
            print('     Wind prep failed')
            return None

    def prep_WL(self, rawWL, timerecord):
        """This function is designed to take the WL packet (in 6 minute averages)
        and create 30/60 minute averages to match the wave record
        samptime is time in minutes of the samples

        Args:
          rawWL (float): input (6 minutes is what is generally used) water level data
          timerecord (datetime object): time record to average/interpolate to

        Returns:
            'name': may return gauge name

            'time': will return time stamp of output data (date time object)

            'avgWL': scalar averaged (temporally interpolated if need be) water level data

            'flag': flags assocated with interpolated data

        """
        try:
            if 'epochtime' not in rawWL:
                rawWL['epochtime'] = nc.date2num(rawWL['time'], 'seconds since 1970-01-01')
            try:  # convert input timerecord to epoch if needed
                timerecord = nc.date2num(timerecord, 'seconds since 1970-01-01')
                if timerecord.dtype == 'int64':
                    temprecord = np.zeros(len(timerecord))
                    for itemp, temp in enumerate(timerecord):
                        temprecord[itemp] = float(temp)
                    timerecord = temprecord
            except:
                pass

            if rawWL != None:
                timeWL = rawWL['epochtime']
                WL = rawWL['WL']
                # remove masked values
                if WL.mask.any():
                    timeWL = np.array(timeWL[~WL.mask]).squeeze()
                    WL = np.array(WL[~WL.mask]).squeeze()

            [trout, avgout, flagOut] = self.scalartimeavg(timerecord, timeWL, WL)
            # __________________________________________________________________
            WLpacket = {'time': [DT.datetime(1970, 1, 1) + DT.timedelta(seconds=float(t)) for t in trout], 'avgWL': avgout,
                        'flag': flagOut}
            if 'name' in rawWL:
                WLpacket['name'] = rawWL['name']

            print('  -- {} WL records with {} interpolated points'.format(np.size(WLpacket['time']),
                                                                          sum(WLpacket['flag'])))

            return WLpacket

        except (RuntimeError, TypeError):
            return None

    def timeLists(d1,d2,dt):
        
        dataTimeList = [d1 + DT.timedelta(seconds=dt * x) for x in
                            range(int((d2 - d1).total_seconds() / float(dt)))]
        return dataTimeList
        
    def createDifferentTimeLists(self, d1, d2, rawSpec, rawWL, **kwargs):
        """ function makes time lists for the simulation for each of the timesteps, Important to note, this adds one
        record to wave time list, as wave records need to be on either side of the flow solution for CMS

        Args:
            d1: start time for simulation
            d2: end time for simulation
            rawSpec: getdatatestbed data package
            rawWL: getdatatestbed data package

        Keyword Args:
            'd1Flow': start of flow simulation different for option of cold start
            'rawWind': a dictionary of wind to include in the process as well

        Returns:
            timeList, waveTimeList, flowTimeList, morphTimeList
            where timelist is the shortest dt of each

        """
        d1Flow = kwargs.get('d1Flow', d1)
        rawWind = kwargs.get('rawWind', None)
        simTs = kwargs.get('simTs',0)

        ############################################################################################                                            
        # flow model requires a wave value on either side of flow time step to bound the flow timestep.  For that                               
        # each of the times are added 1 value                                                                                                   
        if rawSpec is not None:
            # for wave, assume always plus 1 record (cms flow needs to be bound on either side by wave records                                  
            if simTs == 0:
                waveTs = np.median(np.diff(rawSpec['epochtime']))  # time step in seconds of observations                                       
            else:
                waveTs = simTs
            waveTimeList = [d1Flow + DT.timedelta(seconds=waveTs * x) for x in
                            range(int((d2 - d1Flow).total_seconds() / float(waveTs)))]
                            #range(int((1440 / float(waveTs))* (d2 - d1Flow).total_seconds() / float(60 * waveTs)))]                            
        else:
            waveTs = None

        if rawWL is not None:
            if simTs == 0:
                flowTs = np.median(np.diff(rawWL['epochtime']))      # timestep in seconds of WL observations                                   
            else:
                flowTs = simTs
            flowTimeList = [d1Flow + DT.timedelta(seconds=flowTs * x) for x in
                            range(int((d2-d1Flow).total_seconds()/float(flowTs)))]

            morphTs = np.median(np.diff(rawWL['epochtime']))     # timestep in seconds for Morph data save                                      
            morphTimeList = None # [d1 + DT.timedelta(minutes=morphTs * x) for x in range(0, int((1440 / float(morphTs)) * (d2 - d1).total_seconds() / float(60 * morphTs)))]                                                                                                                  
        else:
            morphTs, flowTs, flowTimeList, morphTimeList = None, None, None, None

        # figure out which is highest resolution and return as timelist                                                                         
        TS_list = [waveTs, flowTs, morphTs]




        if rawWind is not None:
            if simTs == 0:
                windTs = np.median(np.diff(rawWind['epochtime']))  # timestep in seconds of WL observations                                     
            else:
                windTs = simTs
            windTimeList = [d1Flow + DT.timedelta(seconds=windTs * x) for x in
                            range(int((d2 - d1Flow).total_seconds() / float(windTs)))]
            TS_list.append(windTs)

        mTS = np.nanmin(np.array(TS_list, dtype=np.float64))
        timeList = [d1Flow + DT.timedelta(seconds=mTS * x) for x in
                    range(int((d2 - d1Flow).total_seconds() / float(mTS)))]  # (1440/float(mTS))*(d2-d1Flow).days +                             

        # Return variables                                                                                                                      
        if rawWind is None:
            windTimeList = None
        return timeList, waveTimeList, flowTimeList, morphTimeList, windTimeList

    def hotStartLogic(self, d1, cmsfio, bathyTime, durationRamp, **kwargs):
        """the begininings of hot start logic
            I need hotstart when not doing a cold start, i need cold start when my runtime is within "simulation Duration"
            of

        Keyword Args:
            verbose: turns on the print statement to let user know what's happening with hotstartLogic

        cmsfio is an instance of the inputOutput class for the model to run
            cmsfio.simulationDuration: runtime in hours for this simulation   (eg 24)
            cmsfio.path: file location for This simulations working directory (eg data/cms/base/20190905T000000Z)
            cmsfio.datestring:  datestring for the simulation
        
        Returns:
            cmsfio: with updated self.datestring, self.bathyDate, self.hotStartFlag
            d1low: start time for the flow model including ramp time
            
        """
        verbose = kwargs.get('verbose', True)
        assert cmsfio.simulationDuration == 24, "this has only been tested using 24 hour simultaions"
        # logic with bathy comparison > 1 is flawed with smaller intervals
        
        datePrevious = sb.whatIsYesterday(d1, stringOut='%Y%m%dT%H%M%SZ', days=cmsfio.simulationDuration / 24)
        hotStartFromPath = os.path.join(os.path.split(cmsfio.path)[0], datePrevious, 'ASCII_HotStart')
        if verbose is True: print('####  ColdSTART LOGIC OUTPUT:') # this is changed and this is what came out
        ######################################################
        if np.size(bathyTime) > 1:   # need to pick what bathy time is before moving forward
            # round bathys to day only
            bathyTime = np.array([DT.datetime.combine(datetime.date(), DT.time(0)) for datetime in bathyTime])
            # look for values that are closest in history
            diffTimesEpoch = np.array([b.timestamp() for b in bathyTime]) - d1.timestamp()
            idx = np.argwhere((max([n for n in (diffTimesEpoch) if n <= 0]) == diffTimesEpoch)).squeeze()
            bathyTime = bathyTime[idx]
        else:  # round bathy time for single occurance
            bathyTime = DT.datetime.combine(bathyTime.date(), DT.time(0))
        # 1. is a hotstart available (look for folder previous with assumption that run duration is the same)
        if os.path.exists(hotStartFromPath):
            # if yes: is there a bathy w/in the time window of the durationRamp
            if verbose is True: print("    found hotstart folder i'm on the right track!")
            if (d1 - bathyTime).total_seconds() > durationRamp*60*60: # if there's no bathy in the ramp window, then take the hotstart, you're clear of confusion
                if verbose is True: print("    No bathy found in the ramp window")
                hotStart = True
            else:
                with open(os.path.join(os.path.split(cmsfio.path)[0], datePrevious, datePrevious+'_cmsfio.pickle'), 'rb') as fid:
                    yesterdaysPickle = pickle.load(fid)
                yesterdaysDatetime = DT.datetime.strptime(yesterdaysPickle.datestring, "%Y%m%dT%H%M%SZ")

                # if there's bathy in the ramp window, we're in a confusing state, we have to look at the last
                # simulation to see if it was cold started, if so we want to pickup where that left off
                if yesterdaysPickle.hotStartFlag is False:
                    hotStart = True
                    if verbose is True: print('    yesterday''s Hotstart was True')
                elif yesterdaysPickle.hotStartFlag is True and yesterdaysDatetime > bathyTime:
                    # if it was hot started, it could be prebathy hotstart or post bathy hotstart
                    # we need to look at the simulation start time and see if it's older than the bathy,
                    # if so then it's a hot start
                    hotStart = True
                    if verbose is True: print('    yesterday''s Hotstart was True and the sim time was AFTER latest bathy time')
                elif yesterdaysPickle.hotStartFlag is True and yesterdaysDatetime <= bathyTime:
                    hotStart = False
                    if verbose is True: print('    yesterday''s Hotstart was False and the sim time was BEFORE latest bathy time')
                else:
                    raise NotImplementedError("hotstart logic isn't working")
        elif bathyTime is not None: # change to last bathy, change d1Flow to be before the last bathy
            # round earlier to nearest simulation duration from last survey
            hotStart = False
            if verbose is True: print('    found NO hotstart available in previous simulation working directory')
        else:
            raise NotImplementedError('Need BathyTime to reset simulation, bathy came in as None')

        ########## clean up and get out ######################################################
        if hotStart is False:
            # start cold start time 1 "duration ramp" before bathyTime
            d1Flow_epoch = bathyTime.timestamp() - DT.timedelta(days=durationRamp).total_seconds()
            d1Flow = DT.datetime.fromtimestamp(d1Flow_epoch)

            # round to nearest simulation duration increment and save new datestring
            # cmsfio.simulationDuration * 3600
            # d1Flow = DT.datetime.fromtimestamp(sb.baseRound(d1Flow_epoch, cmsfio.simulationDuration*3600))
            # cmsfio.datestring = d1Flow.strftime('%Y%m%dT%H%M%SZ')
            # d1Flow = d1Flow - DT.timedelta(days=durationRamp)
        else:
            d1Flow = d1
        if bathyTime > d1:
            raise UnboundLocalError("Your start date is before available bathymetry, please start with a new bathymetry")
        cmsfio.datestring = d1.strftime('%Y%m%dT%H%M%SZ')
        cmsfio.bathyDate = bathyTime    # log what the bathymetery date is.
        cmsfio.hotStartFlag = hotStart  # log hotstartFlag
        if verbose is True and hotStart is True:
            print('    Running HOTSTART with start time of {} instead of {}'.format(d1Flow, d1))
            print('    Due to bathy Time of {} ramp duration of {} day'.format(bathyTime, durationRamp))
            print('    simulation files will be marked with {}\n####   End Hotstart Logic'.format(cmsfio.datestring))
            print(" -------------------- HOTSTART -------------------\n")
        elif verbose is True and hotStart is False:
            print('    Running COLDSTART with NEW start time of {} instead of {}'.format(d1Flow, d1))
            print('    Due to bathy Time of {} ramp duration of {} day'.format(bathyTime, durationRamp))
            print('    simulation files will be marked with {}\n####   End Hotstart Logic'.format(cmsfio.datestring))
            print(" ------------------- COLDSTART -------------------\n")

        # print("cmsfio.read_CMSF_etaDict(hotStartFromPath)\ndurationMod = int(cmsfio.eta_dict['time'])")
        # david's stuff
        # if cmsfio.hotStartFlag is False:  # cold start
        #
        # else:  # hotstart
        #     # look up the hotstart file from the previous run and see how far back we need to pull data for to write the boundary condition file
        #     # load hot-start files
        #     cmsfio.read_CMSF_etaDict(hotStartFromPath)
        #     durationMod = int(cmsfio.eta_dict['time'])
        #     d1Flow = d1 - DT.timedelta(hours=durationMod)

        return cmsfio, d1Flow

    def integrateBathyToBackground(self, data, background, splineDict=None, x_smooth=40, y_smooth=100):
        """This function will integrate bathymetry using plant Scale C interp python
            currently used to integrate cBathy to background grid

        Args:
          data: The new gridded data product, has keys;
             'xFRF'; - coordinates in cross shore postion for FRF local grid

             'yFRF': - coordinates in alongshore position for FRF local grid

             'elevation'; 2d bathymetry elevation to be integrated to background grid

          background: cshore_ncfile of a background grid, will pull keys ['xFRF', 'yFRF'] for background grid points
                to interp to

          splineDict (dict): keys required are below
             'splinebctype': defines type of spline to use
                    2 - second derivative goes to zero at boundary
                    1 - first derivative goes to zero at boundary
                    0 - value is zero at boundary
                    10 - force value and derivative (first?!?) to zero at boundary(Default  = 10)

             'lc': the smoothing scales for the big spline of the entire dataset at the end (rather than just the ends).
                    If this is None it will skip the big spline, smoothing constraint value (usually 4)
                    spline smoothing constraint value (integer <= 1) (Default = 4)
             'dxm': coarsening of the grid (e.g., 2 means calculate with a dx that is 2x input dx)
                    can be tuple if you want to do dx and dy separately (dxm, dym), otherwise dxm is used for both.  (Default = 2)
        
             'dxi': fining of the grid for spline (e.g., 0.1 means return spline on a grid that is 10x input dx)
                    as with dxm, can be a tuple if you want separate values for dxi and dyi (default = 1)

             'off': number of nodes you doing the spline over.  so if off = 5, the spline function will be gernerated
                    between the edge and the node 5 nodes away from the edge.  If handed a tuple it assumes
                    the first value is off_x and the second off_y.  If this is None it will skip the edge spline.
        
             'targetvar': target variance used for spline (Defaut = 0.45)

          x_smooth: this is the smoothing factor from plant in the cross shore direction (Default value = 40) meters

          y_smooth: this is the smoothing factor from plant in the alongshore (Default value = 100) meters

        Returns:
            dictionary with keys below containing integrated bathy

               'xFRF': 1 d array of  frf x coodinate values

               'yFRF': 1 d array of frf y coordiante values

               'elevation': 2d array shaped with xFRF by yFRF elevations are returned in the same datum that they
                    are input and with the same +/- depth convention

        """
        from scaleCinterp_python.DEM_generator import DEM_generator
        from scaleCinterp_python.bsplineFunctions import bspline_pertgrid, DLY_bspline

        if splineDict is None:  # default Spline Parameters
            splinebctype = 10
            lc = 4
            dxm = 2
            dxi = 1
            targetvar = 0.45
            off = 10
        else:
            splinebctype = splineDict['splinebctype']
            lc = splineDict['lc']
            dxm = splineDict['dxm']
            dxi = splineDict['dxi']
            targetvar = splineDict['targetvar']
            off = splineDict['off']
            # build my new bathymetry from grid input in data
        dataX = data['xFRF']
        dataY = data['yFRF']
        dataZ = data['elevation'].squeeze()
        assert np.sign(np.median(dataZ)) == -1, 'data must be positive up convention to match background grid'
        xFRFi_vec = background['xFRF']  # background grid X's
        yFRFi_vec = background['yFRF'] # bacground grid Y's
        Zi = background['elevation']
        dx = np.median(np.abs(np.diff(xFRFi_vec)))
        dy = np.median(np.abs(np.diff(yFRFi_vec)))
        #########################################################################################################
        # what are my subgrid bounds?
        x0 = np.max(dataX)
        y0 = np.max(dataY)
        x1 = np.min(dataX)
        y1 = np.min(dataY)

        # round it to nearest dx or dy
        # minX
        if x1 >= 0:
            x1 = x1 - (x1 % dx)
        else:
            x1 = x1 - (x1 % dx) + dx

        # maxX
        if x0 >= 0:
            x0 = x0 - (x0 % dx)
        else:
            x0 = x0 - (x0 % dx) + dx

        # minY
        if y1 >= 0:
            y1 = y1 - (y1 % dy)
        else:
            y1 = y1 - (y1 % dy) + dy

        # maxY
        if y0 >= 0:
            y0 = y0 - (y0 % dy)
        else:
            y0 = y0 - (y0 % dy) + dy

        # make sure they are inside the bounds of my bigger grid
        # if so, truncate so that it does not exceed.
        # safety first
        if x0 > max(xFRFi_vec):
            x0 = max(xFRFi_vec)
        else:
            pass
        if x1 < min(xFRFi_vec):
            x1 = min(xFRFi_vec)

        if y0 > max(yFRFi_vec):
            y0 = max(yFRFi_vec)

        if y1 < min(yFRFi_vec):
            y1 = min(yFRFi_vec)


        # created x's and y's for all z's
        if (np.shape(dataX) != np.shape(dataY)) or (np.shape(dataX) != np.shape(dataZ)):
            dataX, dataY = np.meshgrid(dataX, dataY)

        # prep dictionary for DEM generator
        dict = {'x0': x0,  # min in x
                'y0': y0,  # min in y
                'x1': x1,  # gp.FRFcoord(x1, y1)['Lon'],  # -75.75004989,
                'y1': y1,  # gp.FRFcoord(x1, y1)['Lat'],  #  36.19666112,
                'lambdaX': dx,  # grid spacing in x
                'lambdaY': dy,  # grid spacing in y
                'msmoothx': x_smooth,  # smoothing length scale in x
                'msmoothy': y_smooth,  # smoothing length scale in y
                'msmootht': 1,  # smoothing length scale in Time
                'filterName': 'hanning',
                'nmseitol': 0.75,
                'grid_coord_check': 'FRF',
                'grid_filename': '',  # this will find the background grid points to load to
                'data_coord_check': 'FRF',
                'xFRF_s': np.reshape(dataX, (np.shape(dataX)[0] * np.shape(dataX)[1], 1)).flatten(),
                'yFRF_s': np.reshape(dataY, (np.shape(dataY)[0] * np.shape(dataY)[1], 1)).flatten(),
                'Z_s': np.reshape(dataZ, (np.shape(dataZ)[0] * np.shape(dataZ)[1], 1)).flatten(),}

        out = DEM_generator(dict)

        # read some stuff from this dict like a boss
        Zn = out['Zi']
        MSEn = out['MSEi']
        MSRn = out['MSRi']
        NMSEn = out['NMSEi']
        xFRFn_vec = out['x_out']
        yFRFn_vec = out['y_out']

        # make my the mesh for the new subgrid
        xFRFn, yFRFn = np.meshgrid(xFRFn_vec, yFRFn_vec)

        # this is telling you where to plop in your new subgrid into your larger background grid
        x1 = np.argwhere(xFRFi_vec == min(xFRFn_vec)).squeeze().astype(int)
        x2 = np.argwhere(xFRFi_vec == max(xFRFn_vec)).squeeze().astype(int)
        y1 = np.argwhere(yFRFi_vec == min(yFRFn_vec)).squeeze().astype(int)
        y2 = np.argwhere(yFRFi_vec == max(yFRFn_vec)).squeeze().astype(int)

        # this is where you pull out the overlapping region from the background
        # so you can take the difference between the original and the subgrid
        Zi_s = Zi[y1:y2 + 1, x1:x2 + 1]

        # get the difference!!!!
        Zdiff = Zn - Zi_s

        # spline time?

        # this is the spline weights that you get from the scale C routine
        # It also incorporates a target variance to bound the weights
        wb = 1 - np.divide(MSEn, targetvar + MSEn)

        # do my edge spline.  if you do Meg's spline afterwards set lc=None!
        # (otherwise it will run its own bspline over the whole thing!!!)
        newZdiff = DLY_bspline(Zdiff, splinebctype=splinebctype, off=off, lc=None)
        # this is Meg's spline of the whole thing
        newZdiff2 = bspline_pertgrid(newZdiff, wb, splinebctype=splinebctype, lc=lc, dxm=dxm, dxi=dxi)
        # add back the new difference to get your new subgrid bathymetry
        newZn = Zi_s + newZdiff2

        # get my new pretty splined grid
        newZi = Zi.copy()
        # replace the subgrid nodes with the new bathymetry
        newZi[y1:y2 + 1, x1:x2 + 1] = newZn

        out = {'xFRF': xFRFi_vec,
               'yFRF': yFRFi_vec,
               'elevation': newZi}

        return out

    def prep_obs2mod(self, obs_time, obs_data, mod_time, removeMask=True):
        """Right now this function just averages observation data over time-windows centered on the times in mod_time.

        Args:
          obs_time: array of observation times.  can be epoch time or datetime
          obs_data: array of observation data corresponding to the observation times
          mod_time: array of times to average the data to. can be epoch time or datetime.
                right now averaging window is 0.5*dt to each side of mod_time.  requires uniform time step
          removeMask: tells it to remove masked data from returned dictionary.
                data will be masked if no observations are found in the time window (Default value = True)

        Returns:
          dictionary with keys:
            'meanObs' - averaged observations

            'stdObs' - observation standard deviation for each time window

            'nObs' - number of observations in each time window

            'time' - times that correspond to the centroid of each time window above

        Notes:
          everything but nObs will be masked if removeMask is False.
          otherwise, the arrays will not be masked but all windows with zero observations will be removed

        """

        # try to convert it from datetime to epochtime
        # this will fail if it already is in epochtime, so it wont do anything.
        dt_check = False
        timeunits = 'seconds since 1970-01-01 00:00:00'
        try:
            obs_time_n = nc.date2num(obs_time, timeunits)
            del obs_time
            obs_time = obs_time_n
            del obs_time_n
        except:
            pass
        try:
            mod_time_n = nc.date2num(mod_time, timeunits)
            del mod_time
            mod_time = mod_time_n
            del mod_time_n
            dt_check = True
        except:
            pass

        # get my time-step
        dt = np.unique(np.diff(mod_time))
        assert np.size(dt) <= 1, 'pre_obs2mod Error: model time must have uniform time-step'

        # loop through my mod_times like a boss
        mask = np.zeros(np.shape(mod_time), dtype=bool)
        avg_data = np.zeros(np.shape(mod_time))
        std_data = np.zeros(np.shape(mod_time))
        n_data = np.zeros(np.shape(mod_time))
        for ii in range(0, len(mod_time)):

            ind = np.where((obs_time >= mod_time[ii] - 0.5*dt) & (obs_time < mod_time[ii] + 0.5*dt))

            if np.size(ind) < 1:
                n_data[ii] = 0
                mask[ii] = True
            else:
                n_data[ii] = np.size(ind)
                avg_data[ii] = np.mean(obs_data[ind])
                std_data[ii] = np.std(obs_data[ind])

        # do I need to convert the time back to datetime?
        if dt_check:
            timeunits = 'seconds since 1970-01-01 00:00:00'
            calendar = 'gregorian'
            time_n = nc.num2date(mod_time, timeunits, calendar)
            del mod_time
            mod_time = time_n
            del time_n

        # create my masked arrays!!!
        avg_data_n = np.ma.array(avg_data, mask=mask)
        std_data_n = np.ma.array(std_data, mask=mask)
        mod_time_n = np.ma.array(mod_time, mask=mask)

        # check if I am removing masked data!
        if removeMask:
            n_data = n_data[~mod_time_n.mask]
            avg_data_n = avg_data_n[~avg_data_n.mask]
            std_data_n = std_data_n[~std_data_n.mask]
            mod_time_n = mod_time_n[~mod_time_n.mask]

        # stick in dictionary
        out = {}
        out['meanObs'] = avg_data_n
        out['stdObs'] = std_data_n
        out['nObs'] = n_data
        out['time'] = mod_time_n
        out['mask'] = mask

        return out

    def dtfun(self, datatime):
        """this function takes different between times

        Args:
          datatime(list):

        Returns:
            np.diff(datatime)
        """
        return np.diff(datatime)

    def insertfun(self, data, dtlist, maxdeadrecord=6, dt=30, axis=0):
        """This function takes the wrong record data and fixes to what it should be by expanding the data size
        according to the dtlist.
        
        Values in dtlist greated than dt will be expanded to make all dt

        Args:
          data: data to be expanded
          dtlist: a lits of dt
          maxdeadrecord: this will not insert more than this number of records to prevent over interpolation (Default=6)
          dt: time (in minutes) the function is looking for to see if the data are needing to be expanded (Default=30)
          axis: axis over which to insert data  (Default value = 0)

        Returns:
            new data:
            flag:
            
        TODO: this function could likely be improved and made more efficient

        """
        # a check to ensure not all data are 0's going in.
        try:
            if (data == 0).all():
                allZeros = True
            else:
                allZeros = False
        except AttributeError:
            allZeros = False
        # defining instertion points
        expandval = [0]
        expandrec = [0]

        for ii in range(0, len(dtlist)):
            assert (dtlist[ii] < DT.timedelta(0,
                    maxdeadrecord * 60 * 60)), 'The Data has too large of a gap to proceed averaging\n ' \
                                               'Change input dates, too large of a gap to fill, default value 6 (hours)'
            if dtlist[ii] > DT.timedelta(0, dt * 60):
                recordadd = int(dtlist[ii].seconds / (dt * 60))
                expandval.append(ii + 1)  # record index to add to
                expandrec.append(recordadd - 1)
            if ii == len(dtlist) - 1:
                expandval.append(np.size(data, axis) + sum(expandrec))  # dtlist is 1 short of total record number of
                expandrec.append(0)

        # creating dummy shape (newdata)
        axes = np.shape(data)
        dim = len(axes)  # how many dimensions is the data
        # this is record placement index variable
        rc = 0

        if dim == 3:
            if axis == 0:
                newdata = np.zeros((axes[0] + sum(expandrec), axes[1], axes[2]))
                flag = np.zeros(np.size(newdata, axis))  # neds to be defined again for all other axis/dims
                if type(data) == list:
                    newdata = newdata.tolist()
                # chopping and placing into dummy new data

                for tt in range(0, np.size(expandval, axis=0)):
                    if tt == np.size(expandval, axis=0) - 1:
                        continue
                    else:
                        newdata[expandval[tt] + expandrec[tt] + rc:expandval[tt + 1] + expandrec[tt] + rc, :, :] = data[
                                                expandval[tt]:expandval[tt + 1], :,:]  # this might need another rc in it
                        if expandrec[tt] > 0:
                            flag[expandval[tt] + rc:expandval[tt] + rc + expandrec[tt]] = 1
                            rc += expandrec[tt]  # summing the values expanded

            elif axis == 1:
                newdata = np.zeros((axes[0], axes[1] + sum(expandrec), axes[2]))
                flag = np.zeros(np.size(newdata, axis))  # neds to be defined again for all other axis/dims

                if type(data) == list:
                    newdata = newdata.tolist()
                    # chopping and placing into dummy new data
                for tt in range(0, np.size(expandval, axis=0)):
                    if tt == np.size(expandval, axis=0) - 1:
                        continue
                    else:
                        newdata[:, expandval[tt] + expandrec[tt] + rc:expandval[tt + 1] + expandrec[tt] + rc, :] \
                            = data[:, expandval[tt]: expandval[tt + 1], :]
                        if expandrec[tt] > 0:
                            flag[expandval[tt] + rc:expandval[tt] + rc + expandrec[tt]] = 1
                            rc += expandrec[tt]  # summing the values expanded
            elif axis == 2:
                newdata = np.zeros((axes[0], axes[1], axes[2] + sum(expandrec)))
                flag = np.zeros(np.size(newdata, axis))  # neds to be defined again for all other axis/dims
                if type(data) == list:
                    newdata = newdata.tolist()
                # chopping and placing into dummy new data
                for tt in range(0, np.size(expandval, axis=0)):
                    if tt == np.size(expandval, axis=0) - 1:
                        continue
                    else:
                        newdata[:, :, expandval[tt] + expandrec[tt] + rc:expandval[tt + 1] + expandrec[tt] + rc] \
                            = data[:, :, expandval[tt]: expandval[tt + 1]]
                        if expandrec[tt] > 0:
                            flag[expandval[tt] + rc:expandval[tt] + rc + expandrec[tt]] = 1
                            rc += expandrec[tt]  # summing the values expanded

        elif dim == 2:
            if axis == 0:
                newdata = np.zeros((axes[0] + sum(expandrec), axes[1]))
                flag = np.zeros(np.size(newdata, axis))  # neds to be defined again for all other axis/dims

                if type(data) == list:
                    newdata = newdata.tolist()
                # chopping and placing into dummy new data
                for tt in range(0, np.size(expandval, axis=0)):
                    if tt != np.size(expandval, axis=0) - 1:
                        newdata[expandval[tt] + expandrec[tt] + rc:expandval[tt + 1] + expandrec[tt] + rc, :]\
                            = data[expandval[tt]:expandval[tt + 1], :]
                        if expandrec[tt] > 0:
                            flag[expandval[tt] + rc:expandval[tt] + rc + expandrec[tt]] = 1
                            rc += expandrec[tt]  # summing the values expanded
            elif axis == 1:
                newdata = np.zeros((axes[0], axes[1] + sum(expandrec)))
                flag = np.zeros(np.size(newdata, axis))  # neds to be defined again for all other axis/dims

                if type(data) == list:
                    newdata = newdata.tolist()
                # chopping and placing into dummy new data
                for tt in range(0, np.size(expandval, axis=0)):
                    if tt != np.size(expandval, axis=0) - 1:
                        newdata[:, expandval[tt] + expandrec[tt] + rc:expandval[tt + 1] + expandrec[tt] + rc]\
                            = data[:, expandval[tt]:expandval[tt + 1]]
                        if expandrec[tt] > 0:
                            flag[expandval[tt] + rc:expandval[tt] + rc + expandrec[tt]] = 1
                            rc += expandrec[tt]  # summing the values expanded

        elif dim == 1:
            if axis == 0:
                newdata = np.zeros((axes[0] + sum(expandrec)))#, dtype=np.int)
                flag = np.zeros(np.size(newdata, axis))  # neds to be defined again for all other axis/dims

                if type(data) == list:
                    newdata = newdata.tolist()
                elif type(data[0]) == DT.datetime:
                    newdata = newdata.tolist()
                # chopping and placing into dummy new data

                for tt in range(0, np.size(expandval, axis=0)):
                    if tt != np.size(expandval, axis=0) - 1:
                        newdata[expandval[tt]+expandrec[tt]+rc:expandval[tt+1]+expandrec[tt]+rc] = data[expandval[tt]:expandval[tt + 1]]
                        if expandrec[tt] > 0:
                            flag[expandval[tt] + rc:expandval[tt] + rc + expandrec[tt]] = 1
                            rc += expandrec[tt]  # summing the values expanded

        # make sure it worked!        \
        if allZeros == False:
            for pp in range(0, np.size(newdata, axis)):
                if flag[pp] != 0:
                    if axis == 0:
                        try:
                            assert (newdata[pp, :, :] == 0).all(), \
                                'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except TypeError:
                            assert (newdata[pp] == 0), \
                                'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except IndexError:
                            if dim == 2:
                                assert (newdata[pp, :] == 0).all(), \
                                    'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                            elif dim == 1:
                                assert (newdata[pp] == 0).all(), \
                                    'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
    
                    elif axis == 1:
                        try:
                            assert (newdata[:, pp, :] == 0).all(),\
                                'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except TypeError:
                            assert (newdata[:][pp] == 0), \
                                'The function is not working correctly. the flag and zeros do not match...\n This assertion was not tested with lists of 2 dimensions. so it may be crap'
                        except:
                            print(' this last data check hasn''t been checked.  your data might be fine')
                    elif axis == 2:
                        try:
                            assert (newdata[:, :, pp] == 0).all(),\
                                'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except TypeError:
                            assert (newdata[:][:][pp] == 0), \
                                'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except:
                            print('this last data check hasn''t been checked, your data COULD be fine, but the inserted record does not check to be in line with the flag')
                elif flag[pp] == 0:
                    if axis == 0:
                        try:
                            assert (newdata[pp, :,
                                    :] != 0).all(), 'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except TypeError:
                            assert (newdata[
                                        pp] != 0), 'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except IndexError:
                            if dim == 2:
                                assert (newdata[pp,
                                        :] != 0).all(), 'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                            elif dim == 1:
                                #try:
                                assert (newdata[
                                            pp] != 0).all(), 'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                                #except AssertionError:
                                #    assert type(newdata[pp]) != np.int64, 'the function has zeros that are the wrong data type, check your flag insertion program'
                    elif axis == 1:
                        try:
                            assert (newdata[:, pp,
                                    :] != 0).all(), 'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except TypeError:
                            assert (newdata[:][
                                        pp] != 0), 'The function is not working correctly. the flag and zeros do not match...\n This assertion was not tested with lists of 2 dimensions. so it may be crap'
                        except:
                            print("this last data check hasn't been checked.  your data might be fine")
                    elif axis == 2:
                        try:
                            assert (newdata[:, :,
                                    pp] != 0).all(), 'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except TypeError:
                            assert (newdata[:][:][
                                        pp] != 0), 'The function is not working correctly.  The flag and inserted record(should be zeros) do not match'
                        except:
                            print('this last data check hasn''t been checked, your data COULD be fine, but the inserted record does not check to be in line with the flag')

        return newdata, flag

    def wlinterp(self, data, flag, axis=0):
        """This function takes data with gaps in the record and does a linear interp between the points
        axis = 0 is the axis upon which to do the linear interpolation
        flag is a 1D list of 1/0 for no data/data

        Probably Better ways to do this

        Args:
          data: data that needs to be interpo;lated, has already had blank records inserted
          flag: input flags letting the fucntion know where to do the interpolation
          axis: axis ver which to do the interpolation (Default value = 0)
        
        Returns:
            linearly interpolated data

        """
        # checking to make sure flags are proper
        a = np.shape(data)  # what is the shape of the data
        # dims=len(a) #how many dimensions are the data
        assert a[axis] == len(flag), 'the interp direction and flag length are different'

        # rolling through flag
        # working just with dim 1 right now
        # setting records
        count = 0
        deadrecord = []
        for ii in range(0, len(flag)):
            if flag[ii] == 0:
                deadrecord.append(count)
                count = 0
            elif flag[ii] == 1:
                count += 1  # remembering how many records to
        # removing zeros
        count = []
        for pp in range(0, len(deadrecord)):
            if deadrecord[pp] != 0:
                count.append(deadrecord[pp])
        # _____Actual interpolation _____

        gapnum = 0
        index = []  # was 0
        for ii in range(0, len(flag)):
            # if flag[ii]==0 and ii==len(flag)  # then get rid of index
            if flag[ii] == 0:
                index.append(ii)  # was +1

        # wave spec type(data)=numpy.ndarray  date time type(data)=list
        if axis == 0:  # 3d wave spectral energy axis0 is time step
            for zz in range(0, len(flag)):  # index:
                if zz != index[-1] and flag[zz] == 0:
                    lastrecord = data[zz]  # establish the last gonselod data set
                elif zz != index[-1] and flag[zz] == 1 and (np.array(data[zz] == 0)).all():
                    nextrecord = data[zz + count[
                        gapnum]]  # count[gapnum] is how many records to advance to find the next non-zero flagged record
                    # this is the incremental value
                    incrementrecord = (nextrecord - lastrecord) / (
                        count[gapnum] + 1)  # the incremental record to add to the last good record (last record)
                    # this is where it adds on over the length gapnum (size of the gap)
                    for qq in range(0, count[gapnum]):
                        if qq == count[gapnum]:
                            assert (data[
                                        zz + qq] == nextrecord).all(), "The interpolation isn't working, the last record doesn't match the interpolated value"
                        else:
                            data[zz + qq] = lastrecord + incrementrecord
                            lastrecord = data[zz + qq]  # record of the last data record
                    if zz != len(flag):
                        gapnum += 1  # advancing to the next gap data se
        else:
            print('there''s no axis !=0 support here')

        return data

    def data_check(self, wavepacket, windpacket, WLpacket, curpacket):
        """this function runs a check comparing the data packets  before the sim file is written
        The times are checked to ensure they are all using the same time stamped data
        
        it will throw an assertion error if they're not
        
        Args:
          wavepacket: dictionary
            time: datetime object to be compared against other data
          windpacket: dictionary
            time: datetime object to be compared against other data
          WLpacket: dictionary
            time: datetime object to be compared against other data
          curpacket: dictionary
            time: datetime object to be compared against other data

        Returns:
            checked data
        """

        #
        # categorizing the data checks by available data
        #
        if wavepacket and windpacket and WLpacket and curpacket != None:
            # missing nothing
            # checking length of records to match
            assert np.size(wavepacket['time']) == np.size(windpacket['windtime']) == np.size(
                WLpacket['WLtime']) == np.size(
                curpacket['curtime']), 'The number of time records must be the same size as time and snapbase'
            assert (np.array(wavepacket['time']) == np.array(windpacket['time'])).all(), 'not the same'
            assert (np.array(wavepacket['time']) == np.array(WLpacket['time'])).all(), 'not the same'
            assert (np.array(wavepacket['time']) == np.array(curpacket['time'])).all(), 'The timestamps are not the same across all packets'
            # have wrong times now do something
            print('Alls checks passed successfully')

        elif wavepacket and windpacket and WLpacket != None:
            # just curpacket is not present
            # checking length of records to match
            assert np.size(wavepacket['time']) == np.size(windpacket['time']) == np.size(
                WLpacket['time']), 'The number of time records must be the same size as time and snapbase'
            assert (np.array(wavepacket['time']) == np.array(windpacket['time'])).all(), 'The timestamps are not the same across all packets'
            assert (np.array(wavepacket['time']) == np.array(WLpacket['time'])).all(), 'The timestamps are not the same across all packets'

            print('Alls checks passed successfully')
        elif wavepacket and windpacket != None:
            # missing currents and WL
            # checking length of records to match
            assert np.size(wavepacket['time']) == np.size(
                windpacket['time']), 'The number of time records must be the same size as wavetime and snapbase'
            # checking for same timestamp on all data
            assert (np.array(wavepacket['time']) == np.array(windpacket['time'])).all(), 'The timestamps are not the same across all packets'

            print('Alls checks passed successfully')
        elif wavepacket and WLpacket != None:
            # missing currents and wind
            # checking length of records to match
            assert np.size(wavepacket['time']) == np.size(
                WLpacket['time']), 'The number of time records must be the same size as wavetime and snapbase'
            # checking for same timestamp on all data
            assert (np.array(wavepacket['time']) == np.array(WLpacket['time'])).all(), 'The timestamps are not the same across all packets'

            print('Alls checks passed successfully')
        elif wavepacket != None:
            # missing everything but waves
            print(' Missing Currents, Wind, and Water Level data')
            # checking for same timestamp on all data

        else:
            print(' You have no data')
            # TODO find delta times for all the records, then do soemthing
            # TODO check to make sure there's no extended gaps in time for any of the records
            # TODO check time increment vs delta time
            # TODO check to make sure the VITAL inputfiles are present in the folder to be written.

    def mod_packets(self, timeList, windpacket, WLpacket, wavepacket=None):
        """This function takes in the packets (wind, wl, wave) and interpolates the data onto the CMS or CMSF time-steps

        NOTE: This function might be redundant as prep wind and prepWL should do this already

        Args:
            timeList: datetime list of times that you want the data to be interpolated onto
            windpacket: windpacket from prep_wind
            WLpacket: water level packet from prep_wl
            wavepacket: wave packet from prep_waves

        Returns
            new windpacket, wlpacket, and wavepacket with the exact same keys as the original packets
                but on a new time-step given by time-list
        """
        assert len(timeList) == len(windpacket['time']) == len(WLpacket['time']), 'Check timing in preprocessing'
        flag = [False, False, False]  # put a check to see if this function ever does anything
        # ok, got my time list already. now lets convert to seconds elapsed
        timeElapsed, tElapsedWL, tElapsedWind = [], [], []
        for ss in range(0, len(timeList)):
            timeElapsed.append((timeList[ss] - timeList[0]).total_seconds())

        for ss in range(0, len(windpacket['time'])):
            tElapsedWind.append((windpacket['time'][ss] - windpacket['time'][0]).total_seconds())

        for ss in range(0, len(WLpacket['time'])):
            tElapsedWL.append((WLpacket['time'][ss] - WLpacket['time'][0]).total_seconds())
        tElapsedWind = np.array(tElapsedWind)
        timeElapsed = np.array(timeElapsed)
        tElapsedWL = np.array(tElapsedWL)

        # modify windpacket
        if not (timeElapsed == tElapsedWind).all():
            newWindP = {}
            newWindP['avgspd'] = np.interp(timeElapsed, tElapsedWind, windpacket['avgspd'])
            newWindP['flag'] = np.interp(timeElapsed, tElapsedWind, windpacket['flag']).astype(int)
            newWindP['avgdir'] = np.interp(timeElapsed, tElapsedWind, windpacket['avgdir'])
            # newWindP['avgdir_CMSF'] = np.interp(timeElapsed, tElapsedWind, windpacket['avgdir_CMSF'])
            newWindP['time'] = timeList
            newWindP['name'] = windpacket['name']
            flag[0] = True
        else:
            newWindP = windpacket

        # modify WL packet
        if not (timeElapsed == tElapsedWL).all():
            newWL = {}
            newWL['avgWL'] = np.interp(timeElapsed, tElapsedWL, WLpacket['avgWL'])
            temp = np.interp(timeElapsed, tElapsedWL, WLpacket['flag'])
            newWL['flag'] = np.array([int(x) for x in temp])
            newWL['time'] = timeList
            newWL['name'] = WLpacket['name']
            flag[1] = True
        else:
            newWL = WLpacket

        if wavepacket is not None:
            tEwave = []
            for ss in range(0, len(wavepacket['time'])):
                tEwave.append((wavepacket['time'][ss] - wavepacket['time'][0]).total_seconds())
            tEwave = np.array(tEwave)
            if not (timeElapsed == tEwave).all():
                # modify wave packet
                newWaveP = {}
                newWaveP['name'] = wavepacket['name']
                newWaveP['time'] = timeList
                # this needs to be timeList converted to string in format 201510010230
                newWaveP['snapbase'] = np.array([DT.datetime.strftime(x, '%Y%m%d%H%M') for x in timeList])
                newWaveP['wavedirbin'] = wavepacket['wavedirbin']
                newWaveP['wavefreqbin'] = wavepacket['wavefreqbin']
                temp = np.interp(timeElapsed, tEwave, wavepacket['flag'])
                newWaveP['flag'] = np.array([int(x) for x in temp])
                newWaveP['peakf'] = np.interp(timeElapsed, tEwave, wavepacket['peakf'])
                # interpolate each frequency/dir bin individually
                rows, cols, deps = np.shape(wavepacket['spec2d'])
                newSpec = np.zeros((len(timeList), cols, deps))
                for ii in range(0, cols):
                    for jj in range(0, deps):
                        newSpec[:, ii, jj] = np.interp(timeElapsed, tEwave, wavepacket['spec2d'][:, ii, jj])
                newWaveP['spec2d'] = newSpec
                flag[2] = True
                wavepacket = newWaveP

        if np.any(flag):
            print("prepData.mod_packets seems to have done something that wasn't previously done")

        return newWindP, newWL, wavepacket

    def prep_dataCMSF(self, windpacketF, WLpacketF, bathy, inputDict, cmsfIO):
        """Preprocess raw data dictionaries to formats that CMSF expects.
        
        This function creates input dictionaries for writing CMS flow IO functions from mod_packets output (time
        matched/interpolated) data for a particular

        Args:
            windpacketF (dict): wind data from mod_packets
            WLpacketF (dict): water level data from mod_packets
            bathy (dict): requires keys 'time' and 'surveyNumber'
            inputDict:
            cmsfIO: an instance of inputouput.cmsf that is pre populated
                cmsfIO.hotStartFlag (bool): True/False denotes hot/cold start sim (default=True)

        Returns:
            cmCards (dict):  input for cmcards file [keys: 'gridAngle', 'gridOriginX', 'gridOriginY', 'simName', 'simulationLabel'
                'telFileName', 'hydroTimestep', 'startingJdate', 'startingJdateHour', 'durationRamp', 'WIND_DIR_CURVE',
                'WIND_SPEED_CURVE', 'hotstartWriteInterval', 'NUM_STEPS', 'WSE_NAME', 'BID_NAME']
            windDirDict(dict): dictionary with wind direction information [keys: 'simName', 'BCtype', 'times', 'values']
            windVelDict (dict): dictionary with wind velocity information [keys: 'simName', 'BCtype', 'times', 'values']
            wlDict (dict): dictionary with waterlevel information       [keys: 'simName', 'BCtype', 'times', 'values', 'cellstringNum']
            cmsfIO (dict): modified instance of cmsf -input output required objects below:
                cmsfIO.simulationDuration: the run duration
                cmsfIO.datestring: a datestring of format '%Y%m%dT%H%M%SZ' to name and look for files
                cmsfIO.hotStartFlag (bool): is this a hotstart or coldstart run
                
        """
        telFile = inputDict['modelSettings'].get('gridTEL', 'grids/CMS/CMS-Flow-FRF.tel')
        surveyNumber = bathy.get('surveyNumber', -999)
        surveyTime = bathy.get('time', -999)
        flowTimeStep = inputDict['flowSettings'].get('flow_time_step', 10) # simulation default time step in minutes
        simulationDuration = cmsfIO.simulationDuration # inputDict['simulationDuration']
        cmsfIO.durationRamp = inputDict['flowSettings'].get('durationRamp', 1)
        durationMod = inputDict['flowSettings'].get('durationMod', 1)
        HSfname = 'ASCII_HotStart'
        path_prefix = inputDict.get('savePath', cmsfIO.path)
        d1 = DT.datetime.strptime(path_prefix.split('/')[-1], '%Y%m%dT%H%M%SZ')
        ######################################################
        date_str = cmsfIO.datestring
        # get wind Prepped
        windTime = [(dt - windpacketF['time'][0]).days * 24 + (dt - windpacketF['time'][0]).seconds / float(3600)
                    for dt in windpacketF['time']]
        
        windDirDict = {'simName': date_str, 'BCtype': 'wind_dir', 'times': windTime,
                       'values': windpacketF['avgdir']}

        windVelDict = windDirDict.copy()
        windVelDict['BCtype'] = 'wind_vel'
        windVelDict['values'] = windpacketF['avgspd']
        # get WL dict prepped
        wlDict = windDirDict.copy()
        wlDict['BCtype'] = 'h'
        wlDict['values'] = WLpacketF['avgWL']
        wlDict['cellstringNum'] = 1
        
        # prep and modify the .tel file
        cmsfIO.read_CMSF_telnc(telFile)
        ugridDict = {'coord_system': 'FRF', 'x': cmsfIO.telnc_dict['xFRF'], 'y': cmsfIO.telnc_dict['yFRF'], 'units': 'm'}
        
        # if i have bathymetry from raw gridded input, interpolate it to unstructured grid
        if bool(bathy) == True:  # empty dictionaries -- when no data -- evaluate to false
            newzDict = gridTools.interpIntegratedBathy4UnstructGrid(ugridDict=ugridDict, bathy=bathy)
            # now replace old depth values with the new ones
            depth = cmsfIO.telnc_dict['depth'].copy()
            newDepth = -newzDict['z']
        
            # if node is inactive, we do not need to replace, set those values to nan
            newDepth[depth <= -999] = np.nan
            # integrate this back into the .tel file
            depth[~np.isnan(newDepth)] = newDepth[~np.isnan(newDepth)]
            del cmsfIO.telnc_dict['depth']
            cmsfIO.telnc_dict['depth'] = depth
            cmsfIO.telnc_dict['surveyNumber'] = surveyNumber
            
        else:  # if this is a hotstart with morpho, the tel file does not need to be updated (same with wave DEP file)
            print('   Running sim with Hotstart Morphology')

    #ONLY THIS IS NEEDED TO WRITE NETcdf TELESCOPE FILE
        cmsfIO.telnc_dict['surveyTime'] = surveyTime
        cmsfIO.telnc_dict['simName'] = date_str


        # write the cmcards dictionary for file writing
        cmCards = {'gridAngle': cmsfIO.telnc_dict['azimuth'],
                   'gridOriginX': cmsfIO.telnc_dict['origin_easting'],
                   'gridOriginY': cmsfIO.telnc_dict['origin_northing'],
                   'simName': date_str,
                   'simulationLabel': 'CMSF_' + date_str,
                   'telFileName': date_str + '.tel',
                   'hydroTimestep': 60*flowTimeStep,
                   'startingJdate': '01001',   # do these need to be modified?
                   'startingJdateHour': 1,
                   'durationRamp': cmsfIO.durationRamp,
                   'WIND_DIR_CURVE': date_str + '_%s' % ('wind_dir') + '.xys',
                   'WIND_SPEED_CURVE': date_str + '_%s' % ('wind_vel') + '.xys',
                   'hotstartWriteInterval': 1,
                   'NUM_STEPS': len(WLpacketF['avgWL']),
                   'WSE_NAME': date_str + '_%s_%s' % ('h', str(int(1))) + '.xys',
                   'BID_NAME': date_str + '.bid'}

        if cmsfIO.durationRamp > 0:
            cmCards['durationRun'] = simulationDuration + 24 * cmsfIO.durationRamp
        else:
            cmCards['durationRun'] = simulationDuration + durationMod


        if cmsfIO.hotStartFlag is True:
            # just copy over the hot start files from the previous day
            datePrevious = d1 - DT.timedelta(0, simulationDuration * 3600, 0)
            date_strPrevious = datePrevious.strftime('%Y%m%dT%H%M%SZ')          # date_str of the previous day
            hotStartFromPath = os.path.join(os.path.dirname(path_prefix), date_strPrevious, HSfname)

            # if bathy is False:  # empty dictionaries evaluate to false
            #     print('do something here?')
            # copy them over to new folder
            writeFolder = os.path.join(cmsfIO.path, HSfname)
            if os.path.exists(writeFolder):
                shutil.rmtree(writeFolder)
            shutil.copytree(hotStartFromPath, writeFolder)

            ## can i glob this folder and iterate on what to do with these files
            # ignore .sup file
            # change datestrings for xy
            hotStartFileList = glob.glob(os.path.join(hotStartFromPath, '*'))
            for fullFname in hotStartFileList:
                fname = os.path.basename(fullFname)
                if fname.endswith('.xy'):
                    cmsfIO.mod_CMSF_HotStart(os.path.join(hotStartFromPath, fname), os.path.join(writeFolder, fname),
                                             searchString='NAME', old_value=date_strPrevious, new_value=date_str)
                elif fname.endswith('.dat'):
                    # for the dat files, change the 48 to
                    cmsfIO.mod_CMSF_HotStart(os.path.join(hotStartFromPath, fname), os.path.join(writeFolder, fname),
                                             searchString='TS 0', old_value='48.0000', new_value=str(
                                             cmsfIO.simulationDuration))
                else:
                    print('     skipped modifying hotstart file {}'.format(fname))
            # # copy over hot start files and change some stuff - DLY 03/18/2019 - this is the one that works
            # cmsfIO.mod_CMSF_HotStart(os.path.join(hotStartFromPath, 'AutoHotStart.xy'),
            #                          os.path.join(writeFolder, 'AutoHotStart.xy'), 'NAME', date_strPrevious, date_str)
            # cmsfIO.mod_CMSF_HotStart(os.path.join(hotStartFromPath, 'SingleHotStart.xy'),
            #                          os.path.join(writeFolder, 'SingleHotStart.xy'), 'NAME', date_strPrevious, date_str)
            # cmsfIO.mod_CMSF_HotStart(os.path.join(hotStartFromPath, 'AutoHotStart_wet.dat'),
            #                          os.path.join(writeFolder, 'AutoHotStart_wet.dat'), 'TS 0', '48.0000', '24.0000')
            # cmsfIO.mod_CMSF_HotStart(os.path.join(hotStartFromPath, 'AutoHotStart_vel.dat'),
            #                          os.path.join(writeFolder, 'AutoHotStart_vel.dat'), 'TS 0', '48.0000', '24.0000')
            # cmsfIO.mod_CMSF_HotStart(os.path.join(hotStartFromPath, 'AutoHotStart_p.dat'),
            #                          os.path.join(writeFolder, 'AutoHotStart_p.dat'), 'TS 0', '48.0000', '24.0000')
            # cmsfIO.mod_CMSF_HotStart(os.path.join(hotStartFromPath, 'AutoHotStart_eta.dat'),
            #                          os.path.join(writeFolder, 'AutoHotStart_eta.dat'), 'TS 0', '48.0000', '24.0000')

            # and tag the cmcards file appropriately
            cmCards['hotstartFile'] = os.path.join(HSfname, 'AutoHotStart.sup')
            
            
            
        return cmCards,  windDirDict, windVelDict, wlDict, cmsfIO

    def getGridDxDyfromDep(self, fname):
        """Will grab dx and dy from STWAVE dep file

        Args:
          fname: file name of dep to get grid parms from

        Returns:
            dictionary with keys below containing general info about grid (no depth values)
            'numrecs' (int): number of records in dep file

            'NI' (int): num of cells in x

            'NJ' (int): num of cells in y

            'dx' (int): cell spacing in x

            'dy' (int): cell spacing in y

            'gridname' (str): grid name (metadata)

        """
        f = open(fname)
        depfile = f.readlines()
        f.close()
        Headerlines = 0
        while depfile[Headerlines].split()[0] != 'IDD':
                Headerlines += 1
        assert depfile[Headerlines].split()[0] == 'IDD', 'The headerlines are wrong for this file, info will not be parsed correctly'

        # begin parsing header data data
        for ii in range(0, Headerlines):
            if depfile[ii].split()[0] == 'NumRecs':
                numrecs= int(depfile[ii].split()[-1][:-1])
            elif depfile[ii].split()[0] == 'NI':
                NI = int(depfile[ii].split()[-1][:-1])
            elif depfile[ii].split()[0] == 'NJ':
                NJ = int(depfile[ii].split()[-1][:-1])
            elif depfile[ii].split()[0] == 'DX':
                dx = float(depfile[ii].split()[-1][:-1])
            elif depfile[ii].split()[0] == 'DY':
                dy = float(depfile[ii].split()[-1][:-1])
            # elif depfile[ii].split()[0] == 'Azimuth':
            #     azi = float(depfile[ii].split()[-1][:-1])
            elif depfile[ii].split()[0] == 'GridName':
                gridname = depfile[ii].split()[-1][:-1]

        dict = {'numrecs': numrecs,
                'NI': NI,
                'NJ': NJ,
                'dx': dx,
                'dy': dy,
                'gridname': gridname,
                #'x0':
                #'y0':
                }
        return dict

    def makeCMSgridNodes(self, x0, y0, azi, dx, dy, z):
        """This interpolates from a node centric coordinate system defined by x0, y0
        to a cell centered values

        Args:
          x0: Grid origin in stateplane
          y0: grid origin in stateplane
          azi: azimuth of the grid
          dx: array of x cell spacings (from ReadCMS_dep)
          dy: array of cell spacings (from ReadCMS_dep)
          z: elevation for dx, dx

        Returns:
          Dictionary with keys:
          'i': cell number for x direction

          'j': cell number for y direction

          'latitude': 2 d array  each cell location in latitude

          'longitude': 2 d array each cell location in longitude

          'easting': 2 d array each cell location in NC stateplane easting

          'northing': 2d array each cell location in NC stateplane northing

          'xFRF': FRF x coordinate values

          'yFRF': FRF y coordinate values

          'azimuth': grid azimuth

          'x0': grid origin x

          'y0': grid origin y

          'elevation': 2 d array of elevations ( positive down )

          'time': time of the grid in epoch time ( 0 is fill value) - currently set

        """
        # convert from node calculation to centric calculation
        # first move origin from vertex of grid to center of first grid cell

        # first convert to FRF coordinates
        FRF = gp.FRFcoord(x0, y0)
        # shift origin to cell center instead of cell vertex
        x0N = FRF['xFRF'] - dx[0]/2
        y0N = FRF['yFRF'] - dy[0]/2
        # create new dx/dy array
        dxN = dx[:-1] + np.diff(dx)/2
        dyN = dy[:-1] + np.diff(dy)/2 # new nodes at the grid center - needed to fit into
        # create new nodes in FRF x and FRF Y using cell centric locations for accurate interpolation
        outXfrf, outYfrf = createGridNodesinFRF(x0N, y0N, dxN, dyN, dx.shape[0], dy.shape[0])
        xFRF, yFRF = np.meshgrid(outXfrf, sorted(outYfrf))

        # new work no need to loop as above
        convert2 = gp.FRFcoord(xFRF.flatten(), yFRF.flatten(), coordType='FRF')
        lat = convert2['Lat'].reshape(xFRF.shape)
        lon = convert2['Lon'].reshape(xFRF.shape)
        easting = convert2['StateplaneE'].reshape(xFRF.shape)
        northing = convert2['StateplaneN'].reshape(yFRF.shape)
        # making i's and j's for cell numbers
        ii = np.linspace(1, xFRF.shape[1], xFRF.shape[1])
        jj = np.linspace(1, yFRF.shape[0], yFRF.shape[0])

        # flipping z so it matches x and y (increasing in x & y)
        # it was read starting at i =0 and j=nj which is backwards from FRF coordinates
        # this is taken care of in the bathy Load file

        BathyPacket = {'i': ii,
                       'j': jj,
                       'latitude': lat,
                       'longitude': lon,
                       'easting': easting,
                       'northing': northing,
                       'xFRF': sorted(xFRF[0, :]),
                       'yFRF': yFRF[:, 0],
                       'azimuth': azi,
                       'x0': x0,
                       'y0': y0,
                       'DX': dxN,
                       'DY': dyN,
                       'ni': len(ii),
                       'nj': len(jj),
                       'elevation': z,  # exported as [t, x,y] dimensions
                       # 'bathy': -np.expand_dims(z, axis=0),
                       'gridFname': 'CMS GRid',
                       'time': 0}

        return BathyPacket

    def prep_SwashBathy(self, x0, y0, bathy, yBounds, **kwargs):
        """Takes in bathy dictionary from get bathy data

        Args:
            x0 (float): cross-shore location of computational grid origin (xFRF location of gauge)
            y0 (float); alongshore location of computational grid origin (yFRF location of gauge)
            bathy (dict): a dictionary with required keys
                'xFRF': x coordinate in FRF

                'yFRF': y coorindate in FRF

                'elevation': bathymetry

            yBounds(list): a list of size two that describes the bounds in the alongshore direction,
                    defaults to cross-shore array (Default=[940, 950])

        Keyword Args:
            'dx'(float): resolution in x (default = 1 m)
            'dy'(float): resolution in y (default = 1 m)
            'xBounds'(list): cross-shore bounds of domain (Default=[25, 915])
            
        Returns:
            swsPacket(dict):
                'mx'(int): number of mesh's in xCoord
                'my'(int): number of mesh's in yCoord
                'dx':  mesh/grid resolution [m]
                'dy':  mesh/grid resolution [m]
                'xpc': origin of computational grid in larger coord
                'ypc':  origin of computational grid in larger coord
                'alpc': orientation of grid (degrees counter clockwise rotation from true North), to larger coord (
                                                default = 0)

            bathyOut(dict)
                "elevation": interpolated bathymetry
                "xFRF": new xFRF values
                "yFRF": new yFRF values
        """

        #  mesh/grid resolution [m] set default resolution
        dx = kwargs.get('dx', 0.5)
        dy = kwargs.get('dy', 0.5)
        xbounds = kwargs.get('xBounds', [25, 915])
        alpc = kwargs.get('alpc', 0)              # degrees counter clockwise rotation from true North
        xpc = x0                                  # origin of computational grid in larger coord
        ypc = y0                                  # origin of computational grid in larger coord

        mx = np.squeeze(np.diff(xbounds)/dx).astype(int)      # number of mesh outputs
        my = np.squeeze(np.diff(yBounds)/dy).astype(int)      # number of mesh outputs


        if my <3: my=3
        if np.size(bathy['yFRF']) != my:
            bathy['yFRF'] = np.arange(yBounds[0], yBounds[1], dy)
            bathy['elevation'] = np.tile(bathy['elevation'], (my, 1))
            print('  made 1D bathy')
            
        ###  now interp bathy linearly to dx, dy
        f = interpolate.interp2d(bathy['xFRF'], bathy['yFRF'], bathy['elevation'], fill_value=None, bounds_error=False)
        #newXFRF = np.linspace(0, np.round(x0), int(mx), endpoint=True)

        # had to change endpoint to false for SWASH setup
        newXFRF = np.linspace(xbounds[0], xbounds[1], num=int(mx), endpoint=False)
        newYFRF = np.linspace(yBounds[0], yBounds[1], num=int(my), endpoint=False)
        # xx, yy = np.meshgrid(newXFRF, newYFRF)
        interpedBathy = f(newXFRF,  newYFRF)
        
        # bathy corresponding mx = 1 length
        swsPacket = {'mx':   mx,
                     'my':   my,
                     'dx':   dx,
                     'dy':   dy,
                     'xpc':  xpc,
                     'ypc':  ypc,
                     'alpc': alpc,
                     'elevation': interpedBathy,
                     'xFRF': newXFRF,
                     'yFRF': newYFRF}
        return swsPacket

    def GetOriginalGridFromSTWAVE(self, yesterdaysSim, yesterdaysDEP):
        """This function makes a data packet from which a netCDF file can be made,
        It reads in a dep and a Sim file to create the data packet

        Args:
          yesterdaysSim: STWAVE sim file name to open
          yesterdaysDEP: STWAVE dep file name to open

        Returns:
          a dictionary with keys
            'latitude': latitude of cell nodes

            'longitude': longitude of cell nodes

            'easting': north carolina state plane of cell nodes

            'northing': north carolina state plane of cell nodes

            'xFRF': x location of cell nodes

            'yFRF': y location of cell nodes

            'bathy': elevation values

            'azimuth': grid orientation

            'x0': grid origin (NC stateplane)

            'y0': grid origin (NC stateplane)

            'DX': cell spacing in x

            'DY': cell spacing in y

            'NI': number of cells in x

            'NJ': number of cells in y

            'gridFname'(str): grid name (metadata)

            'time': time pulled from grid name with assumption of key 'SurveyDate_' in the grid name. will assume a
                format of  '%Y-%m-%dT%H%M%SZ' or %Y-%m-%d

        """
        from prepdata import inputOutput

        stio = inputOutput.stwaveIO('')
        gridParms = stio.simLoad(stwaveSimFile=yesterdaysSim)
        # coords = gp.ncsp2FRF(gridParms['x0'], gridParms['y0'])  # in hopes of making below more efficient
        # outIfrf2, outJfrf2 = createGridNodesinFRF(coords['xFRF'], coords['yFRF'],
        #                                           np.tile(gridParms['dx'], gridParms['ni']),
        #                                           np.tile(gridParms['dy'], gridParms['nj']),
        #                                           gridParms['ni']-1, gridParms['nj']-1) # minus 1 to deal with 0 index
        iStatePlane, jStatePlane = CreateGridNodesInStatePlane(gridParms['x0'], gridParms['y0'], gridParms['azi'],
                                                               gridParms['dx'], gridParms['dy'], gridParms['ni'], gridParms['nj'])

        outIfrf, outJfrf = convertGridNodesFromStatePlane(iStatePlane, jStatePlane)
        # i has to be sorted to flip from offshore origin to onshore origin in x direction
        # j is sorted to move coordinate system from top to bottom of property
        # (still in RH coordinate system)
        xs = sb.baseRound(outIfrf[:, 0], gridParms['dx'])  # fix back to dx's and y's
        ys = sb.baseRound(outJfrf[:, 1], gridParms['dy'])
        xFRF, yFRF = np.meshgrid(sorted(xs), sorted(ys))

        convert2 = gp.FRFcoord(xFRF.flatten(), yFRF.flatten(), coordType='FRF')
        lat = convert2['Lat'].reshape(xFRF.shape)
        lon = convert2['Lon'].reshape(xFRF.shape)
        easting = convert2['StateplaneE'].reshape(xFRF.shape)
        northing = convert2['StateplaneN'].reshape(yFRF.shape)

        stio.depfname_nest = [yesterdaysDEP]
        DEPpacket = stio.DEPload(nested=True)
        # elevation = -DEPpacket['bathy']  # flip depths to elevations (sign convention)

        gridNameSplit = DEPpacket['gridFname'].split('_')
        if 'SurveyDate' in gridNameSplit:
            bathyDateA = gridNameSplit[np.argwhere(np.array(gridNameSplit[:]) == 'SurveyDate').squeeze() + 1]
            # making the bathymetry grid
            try:
                bathyTime = DT.datetime.strptime(bathyDateA, '%Y-%m-%dT%H%M%SZ')
            except ValueError:
                try:
                    bathyTime = DT.datetime.strptime(bathyDateA, '%Y-%m-%d')
                except:
                    bathyTime = nc.num2date(-1e6, 'seconds since 1970-01-01')  # set to rediculous value
        else:
            bathyTime = nc.num2date(-1e6, 'seconds since 1970-01-01')
        yesterdaysBathyPacket = {'latitude': lat,
                                 'longitude': lon,
                                 'easting': easting,
                                 'northing': northing,
                                 'xFRF': xFRF[0, :],  # xFRF[0, :],
                                 'yFRF': yFRF[:, 0],
                                 'bathy': DEPpacket['bathy'],
                                 'azimuth': gridParms['azi'],
                                 'x0': gridParms['x0'],
                                 'y0': gridParms['y0'],
                                 'DX': DEPpacket['dx'],
                                 'DY': DEPpacket['dy'],
                                 'NI': DEPpacket['NI'],
                                 'NJ': DEPpacket['NJ'],
                                 'gridFname': DEPpacket['gridFname'],
                                 'time': bathyTime}
        return yesterdaysBathyPacket

    def Fixup17mGrid(version_prefix, wave_pack, dep_pack, Tp_pack, fill_value=np.nan):
            """This function is designed to add filler data to size the truncated grid that's created with the offshore
            boundary is initalized from the 17m waverider not the 26m waverider,  data output from the model are placed
            into filled arrays with the fill value default in this function

            Args:
                version_prefix (str): version prefix associated with output data, function uses this to pull full
                    grid data (shape, cell coordinates, etc)
                wave_pack (dict): will look for
                dep_pack (dict):
                Tp_pack (dict):
                fill_value: will use this fill value to fill arrays where the model did not produce data (defaule=np.nan)

            Returns:
                new dictionaries that are the size of the full data arrays, using fill values

            """
            ncfile = nc.Dataset('http://bones/thredds/dodsC/cmtb/waveModels/STWAVE/{}/Regional-Field/Regional-Field.ncml'.format(version_prefix))
            NJ, NI =  ncfile['waveHs'].shape[1:]
            fill = np.ones((wave_pack['Hs_field'].shape[0], NJ, NI)) * fill_value
            # replace all the field values with the filled, value to the same dim
            # start with wave_pack
            for var in list(wave_pack.keys()):
                if var.split('_')[-1].lower() == 'field':
                    fill[:, :, slice(0, wave_pack[var].shape[2])] = wave_pack[var]
                    wave_pack[var] = fill
            # fill dep_pack
            for var in list(dep_pack.keys()):
                if var.split('_')[-1].lower() == 'bathy':
                    fill[:, :, slice(0, dep_pack[var].shape[2])] = dep_pack[var]
                    dep_pack[var] = fill
                elif var in ['yFRF', 'xFRF']:
                    dep_pack[var] = ncfile[var][:]
            try:
                dep_pack['longitude'] = ncfile['longitude'][:]
                dep_pack['latitude'] = ncfile['latitude'][:]
            except IndexError:
                pass
            dep_pack['NI'] = NI  # reset the dimensions so its written properly
            dep_pack['NJ'] = NJ  # reset dims
            # finally Tp
            fill[:, :, slice(0, Tp_pack['Tp_field'].shape[2])] = Tp_pack['Tp_field']
            Tp_pack['Tp_field'] = fill
    
            return wave_pack, dep_pack, Tp_pack

    # doctor up CMSF results files to go into netCDF form

    def modCMSFsolnDict(self, solnDict, telDict, timeStepCount, **kwargs):
        """Post process CMS flow simulation variables.
        
        Take the CMSFwrite dictionary (solnDict) and re-arrange it so that it fits on the
        exact cellID order of the .tel file. Then pad the arrays with fill values where the .tel depth is
        -999 - i.e., masked

        Args:
            solnDict: dictionary with below keys
                aveN - average north velocity in each cell
                aveE - average east velocity in each cell
                durationRamp - ramp duration for this simulation
                time - time of each time-step in this beast in epoch-time
                waterLevel - water level in each active cell

            telDict: # note - this needs to be the cio.telnc_dict for this to work.  cio.tel_dict doesn't have
                          surveyNumber and surveyTime
                relavent keys:
                cellID - cell ID of every node in the .tel file
                depth - depth of every node in the .tel file
                surveyNumber - survey number of the survey that went into this .tel file
                surveyTime - time of the survey that went into this .tel file

            timeStepCount: number of hours this simulation is supposed to run - this is fron the inputDict that is
                written from the input yaml file
        
        Keyword Args:
            "morphPack": input morphology dictionary with data (default=None)
            'maskValue': maskValue for netCDF file
            
        Returns:
            newSolnDict - will add depth, surveyNumber, and surveyTime from the telDict to the keys
            will also take the solnDict cells and order them onto the cellID array from the .tel file
            so they all match up values with -999 depth will be masked

        """
        morphPack = kwargs.get('morphPack', None)
        maskValue = kwargs.get('maskValue', -999)
        # okay, this is SUPER IMPORTANT! - NO NO NO, I think this is WRONG!
        # IF the solutions (i.e., velocities and water level) are indexed the SAME as the .xy file, THEN
        # the cellID's of the solutions are the non -999 .tel file cellID's in REVERSE!
        # so, the large cellID's are first
        # solnDict['cellID'] = np.flip(telDict['cellID'][telDict['depth'] != -999], 0)

        # is it the other way around ?
        # if we JUST take a look at the plots and IGNORE whats in the .xy file,
        # then it appears like it should NOT be in reverse? DLY 06/20/2018
        solnDict['cellID'] = telDict['cellID'][telDict['depth'] != maskValue]

        # get the surveyNumber and surveyTime from the telDict
        surveyTime = telDict['surveyTime']
        surveyNumber = telDict['surveyNumber']

        [rows, _] = np.shape(solnDict['aveN'])


        cellIDn = telDict['cellID']
        depthn = telDict['depth']
        numberCellsn = telDict['numberCells']
        # durationRampn = solnDict['durationRamp']
        timen = solnDict['time']

        # # match time - I think this could be done faster if I thought about it more...
        # for ss in range(0, len(telDict['cellID'])):
        #     # check to see if this cell is in the solution
        #     if cellIDn[ss] in solnDict['cellID']:
        #         ind = np.where(solnDict['cellID'] == cellIDn[ss])
        #         aveEn[:, ss] = solnDict['aveE'][:, ind].flatten()
        #         aveNn[:, ss] = solnDict['aveN'][:, ind].flatten()
        #         waterLeveln[:, ss] = solnDict['waterLevel'][:, ind].flatten()

        # identify which cells in the intital grid are fill values
        idxSoln = np.in1d(telDict['cellID'], solnDict['cellID'])
        # write aveE, aveN, waterLevel

        aveEn = np.ones((timeStepCount, len(telDict['cellID']))) * maskValue
        aveNn = np.ones((timeStepCount, len(telDict['cellID']))) * maskValue
        waterLeveln = np.ones((timeStepCount, len(telDict['cellID']))) * maskValue  # mask value is -999 for WL
        # write values from soln grid to full grid leaving fill values where there is no data
        waterLeveln[:, idxSoln] = solnDict['waterLevel'][-timeStepCount:, :]
        aveEn[:, idxSoln] = solnDict['aveE'][-timeStepCount:, :]
        aveNn[:, idxSoln] = solnDict['aveN'][-timeStepCount:, :]
        
        # IMPORTANT NOTE - WL can be -999 even in .tel file cells that ARE NOT masked (i.e., depth != -999)
        # THIS MEANS that if you are comparing the WL mask and the depth mask in the written out nc file they MAY NOT
        # be the same

        # take ONLY the last "timeStepCount" hours of stuff
        newSolnDict = {'aveN':         aveNn,
                       'aveE':         aveEn, # [int(-timeStepCount):, :],  # for old way
                       'time':         timen[int(-timeStepCount):],
                       'waterLevel':   waterLeveln, # for old way [int(-timeStepCount):, :],
                       #'durationRamp': durationRampn
                       'numberCells': numberCellsn,
                       'cellID': cellIDn,
                       'surveyNumber': surveyNumber,
                       'surveyTime': surveyTime,
                       'depth': depthn,
                        }
        if morphPack is not None:
            # initalize output for morphology
            dzb = np.ones_like(aveNn) * maskValue
            depth = np.ones_like(aveNn) * maskValue
            Qb = np.ones((timeStepCount, len(telDict['cellID']), 2)) * maskValue
            # write values from soln grid to full grid leaving fill values where there is no data
            dzb[:, idxSoln] = morphPack['dzbDict']['data'][-timeStepCount:, :]
            depth[:, idxSoln] = morphPack['depDict']['data'][-timeStepCount:, :]
            Qb[:, idxSoln] = morphPack['QbDict']['data'][-timeStepCount:, :]
            # write full array to output dictionary
            newSolnDict['depth'] = depth
            newSolnDict['dzb'] = dzb
            newSolnDict['QbE'] = Qb[:, :, 1]  # these vectors are un tested, may need to be switched or multiplied by
            newSolnDict['QbN'] = Qb[:, :, 0]  # cos/sine grid angle
            
        return newSolnDict

    def prep_CSHOREwaves(self, wavepacket, elapsed, start_time, pierAng=71.8):
        """This function is designed to prep the wave data from getdata to that it can go into a CSHORE run
        
        It DOES NOT pull the data itself or figure out which gauge is necessary.
        this is to avoid calls to getdata inside of prepdata
        
        Args:
             wavepacket:  this is just a wavepacket output from getWaveSpec
             elapsed: this is the amount of time that has that has elapsed from the model start in seconds
             start_time: this is the datetime of the model start
        
        Returns:
             a dictionary that has all the keys we need to assign to
                BC_dict and meta_dict once we get out of this function
        """
        o_dict = {}
        o_dict['BC_gage'] = wavepacket['name']

        # build my times list
        #print(elapsed)
        times = [start_time + DT.timedelta(seconds=tt) for tt in elapsed]

        # new check for my waves need to bomb out
        # enough points before
        tb = wavepacket['time'][np.where(wavepacket['time'] <= times[0])]
        assert np.size(tb) >= 1, 'Error: wave data missing for simulation start time'
        # enough points after
        ta = wavepacket['time'][np.where(wavepacket['time'] >= times[-1])]
        assert np.size(ta) >= 1, 'Error: wave data missing for simulation end time'
        # max diff is not too large
        assert np.size(np.where(np.diff(wavepacket['time']) > DT.timedelta(days=0, hours=6, seconds=0))) < 1, 'Error: gaps in wave data > 6 hours'


        # get missing wave data if there is any!
        dum_var = [x not in wavepacket['time'] for x in times]
        if sum(dum_var) == 0:
            o_dict['blank_wave_data'] = []
            print("%d wave records with %d interpolated points" % (np.shape(wavepacket['Hs'])[0], 0))
        else:
            o_dict['blank_wave_data'] = [times[tt] for tt in np.argwhere(dum_var).flatten()]  # this will list all the times that wave data should exist, but doesn't
            print("%d wave records with %d interpolated points" % (np.shape(wavepacket['Hs'])[0], len(o_dict['blank_wave_data'])))

        helper = np.vectorize(lambda x: x.total_seconds())
        o_dict['Hs'] = np.interp(elapsed, helper(wavepacket['time'] - wavepacket['time'][0]), wavepacket['Hs'])  # WE ARE USING Hmo (Hs in wave_data dictionary) INSTEAD OF Hs!!!!! -> convert during infile write!!!
        try:
            o_dict['Tp'] = np.interp(elapsed, helper(wavepacket['time'] - wavepacket['time'][0]), wavepacket['Tp'])
        except:
            o_dict['Tp'] = np.interp(elapsed, helper(wavepacket['time'] - wavepacket['time'][0]), np.divide(1, wavepacket['peakf']))  # we are inverting the peak frequency to get peak period

        o_dict['angle'] = np.interp(elapsed, helper(wavepacket['time'] - wavepacket['time'][0]), anglesLib.geo2STWangle(wavepacket['waveDp'], zeroAngle=pierAng, fixanglesout=1))  # i am assuming that the angle is the peak of the directional spectra, not the MEAN ANGLE!!!  also I'm assuming 0-360 degrees!
        o_dict['lat'] = wavepacket['lat']
        o_dict['lon'] = wavepacket['lon']

        return o_dict

    def prep_CSHOREbathy(self, bathypacket, bathytype, dx, wavepacket, profile_num=0, fric_fac=0):

        """
        his function is designed to prep the bathy data from getdata to that it can go into a CSHORE run
        It DOES NOT pull the data itself to avoid calls to getdata inside of prepdata
        :param bathypacket: this is the bathymetry packet from getdata, either getBathyIntegratedTransect for integrated bathy or getBathyTransectFromNC for surveys
        :param bathytype: this is the type of bathy packet that was handed to it, either 'survey' or 'integrated_transect'
        :param profile_num: this is the profile number or the along-shore position in the integrated transect that you want for the bathy
        :param dx: this is the spacing of the bathymetry in the model
        :param wavepacket: this is the wavepacket with the wave data, it needs this for the boundary position
        :param fric_fac: this is the friction factor to be set for the bed.
        :return: a dictionary that has all the keys that the metadata dictionary and the boundary condition dictionary need related to the bathymetry
        """

        assert bathytype in ['survey', 'integrated_bathy', 'prior_model', 'xyz'], "Error: this bathymetry type is not supported"
        assert bathypacket is not None, 'Simulation broken.  Bathymetry data not assigned!'

        b_dict = {}

        if bathytype == 'survey':
            # calculate some stuff about the along-shore variation of your transect!
            b_dict['bathy_surv_num'] = np.unique(bathypacket['surveyNumber'])  # tag the survey number!
            b_dict['bathy_surv_stime'] = bathypacket['time'][0]  # tag the survey start time!
            b_dict['bathy_surv_etime'] = bathypacket['time'][-1]  # tag the survey end time!
            b_dict['bathy_prof_num'] = profile_num  # tag the profile number!
            b_dict['bathy_y_max_diff'] = bathypacket['yFRF'].max() - bathypacket['yFRF'].min()  # what is the difference between the largest y-position of this transect and the smallest y-position of this transect in FRF coordinates (FRF units)
            b_dict['bathy_y_sdev'] = np.std(bathypacket['yFRF'])  # standard deviation of the y-positions of this transect in FRF coordinate (FRF units)

            master_bathy = {'xFRF': np.asarray(list(range(int(math.ceil(min(bathypacket['xFRF']))), int(max(bathypacket['xFRF']) + dx), dx)))}  # xFRF coordinates of master bathy indices in m
            master_bathy['elev'] = np.interp(master_bathy['xFRF'], bathypacket['xFRF'], bathypacket['elevation'])  # elevation at master bathy nodes in m

            # actually convert the bathy_data to the coordinates of the model!
            bc_coords = gp.FRFcoord(wavepacket['lon'], wavepacket['lat'])
            b_dict['BC_FRF_X'] = int(round(bc_coords['xFRF']))  # this is because I force the gauge to be at a grid node
            b_dict['BC_FRF_Y'] = bc_coords['yFRF']
            # check that the gauge is inside my "master_bathy" x bounds
            assert bc_coords['xFRF'] <= max(master_bathy['xFRF']) and bc_coords['xFRF'] >= min(master_bathy['xFRF']), 'The wave gauge selected as the boundary condition is outside the known bathymetry.'

            # make the shift from "master bathy" to model bathy convention (zero at forcing instrument and positive increasing towards shore)
            b_dict['x'] = np.flipud(int(round(bc_coords['xFRF'])) - master_bathy['xFRF'][np.argwhere(master_bathy['xFRF'] <= int(round(bc_coords['xFRF'])))].flatten())
            b_dict['zb'] = np.flipud(master_bathy['elev'][np.argwhere(master_bathy['xFRF'] <= int(round(bc_coords['xFRF'])))].flatten())
            b_dict['fw'] = np.flipud(fric_fac * np.ones(b_dict['x'].size))  # cross-shore values of the bottom friction (just sets it to be fric_fac at every point in the array)

        elif bathytype == 'integrated_bathy':
            # get my master bathy x-array
            master_bathy = {'xFRF': np.asarray(list(range(int(math.ceil(min(bathypacket['xFRF']))), int(max(bathypacket['xFRF']) + dx), dx)))}  # xFRF coordinates of master bathy indices in m
            elev_mat = bathypacket['elevation']
            xFRF_mat = npmat.repmat(bathypacket['xFRF'], np.shape(elev_mat)[0], 1)
            yFRF_mat = npmat.repmat(bathypacket['yFRF'].T, np.shape(elev_mat)[1], 1).T

            # have to do 2D interpolation instead of 1D!!!!!!
            points = np.array((xFRF_mat.flatten(), yFRF_mat.flatten())).T
            values = elev_mat.flatten()
            interp_pts = np.array((master_bathy['xFRF'], profile_num * np.ones(np.shape(master_bathy['xFRF'])))).T
            master_bathy['elev'] = interpolate.griddata(points, values, interp_pts)

            # calculate some stuff about the along-shore variation of your transect!
            b_dict['bathy_surv_num'] = np.unique(bathypacket['surveyNumber'])  # tag the survey number!
            b_dict['bathy_surv_stime'] = bathypacket['time']  # same for integrated bathy
            b_dict['bathy_surv_etime'] = bathypacket['time']  # same for integrated bathy
            b_dict['bathy_prof_num'] = profile_num  # tag the profile number!
            b_dict['bathy_y_max_diff'] = 0  # always zero for intergrated bathy
            b_dict['bathy_y_sdev'] = 0  # always zero for intergrated bathy

            # actually convert the bathy_data to the coordinates of the model!
            bc_coords = gp.FRFcoord(wavepacket['lon'], wavepacket['lat'])
            b_dict['BC_FRF_X'] = int(round(bc_coords['xFRF']))  # this is because I force the gauge to be at a grid node
            b_dict['BC_FRF_Y'] = bc_coords['yFRF']
            # check that the gauge is inside my "master_bathy" x bounds
            assert bc_coords['xFRF'] <= max(master_bathy['xFRF']) and bc_coords['xFRF'] >= min(master_bathy['xFRF']), 'The wave gauge selected as the boundary condition is outside the known bathymetry.'

            # make the shift from "master bathy" to model bathy convention (zero at forcing instrument and positive increasing towards shore)
            b_dict['x'] = np.flipud(int(round(bc_coords['xFRF'])) - master_bathy['xFRF'][np.argwhere(master_bathy['xFRF'] <= int(round(bc_coords['xFRF'])))].flatten())
            b_dict['zb'] = np.flipud(master_bathy['elev'][np.argwhere(master_bathy['xFRF'] <= int(round(bc_coords['xFRF'])))].flatten())
            b_dict['fw'] = np.flipud(fric_fac * np.ones(b_dict['x'].size))  # cross-shore values of the bottom friction (just sets it to be fric_fac at every point in the array)

        elif bathytype == 'prior_model':

            meta0 = bathypacket['meta0']
            morpho0 = bathypacket['morpho0']

            # calculate some stuff about the along-shore variation of your transect!
            b_dict['bathy_surv_num'] = meta0['bathy_surv_num']
            b_dict['bathy_surv_stime'] = meta0['bathy_surv_stime']
            b_dict['bathy_surv_etime'] = meta0['bathy_surv_etime']
            b_dict['bathy_prof_num'] = meta0['bathy_prof_num']  # tag the profile number!
            b_dict['bathy_y_max_diff'] = meta0['bathy_y_max_diff']  # what is the difference between the largest y-position of this transect and the smallest y-position of this transect in FRF coordinates (FRF units)
            b_dict['bathy_y_sdev'] = meta0['bathy_y_sdev']  # standard deviation of the y-positions of this transect in FRF coordinate (FRF units)

            b_dict['BC_FRF_X'] = meta0["BC_FRF_X"]
            b_dict['BC_FRF_Y'] = meta0["BC_FRF_Y"]

            b_dict['x'] = morpho0['x'][-1]
            b_dict['zb'] = morpho0['zb'][-1]
            b_dict['fw'] = np.flipud(fric_fac * np.ones(b_dict['x'].size))
        elif bathytype == 'xyz':
            # calculate some stuff about the along-shore variation of your transect!
            b_dict['bathy_surv_num'] = 0  # tag the survey number!
            b_dict['bathy_surv_stime'] = DT.datetime.utcnow()  # tag the survey start time!
            b_dict['bathy_surv_etime'] = DT.datetime.utcnow()  # tag the survey end time!
            b_dict['bathy_prof_num'] = 0  # tag the profile number!
            b_dict['bathy_y_max_diff'] = 0
            b_dict['bathy_y_sdev'] = 0

            master_bathy = {'xFRF':np.arange(np.floor(min(bathypacket[:,0])), np.ceil(max(bathypacket[:,0]))+dx,dx)}
            #master_bathy = {'xFRF': np.asarray(list(
            #    range(int(math.ceil(min(bathypacket[:,0]))), int(max(bathypacket[:,0]) + dx),
            #          dx)))}  # xFRF coordinates of master bathy indices in m
            master_bathy['elev'] = np.interp(master_bathy['xFRF'], bathypacket[:,0],
                                             bathypacket[:,1])  # elevation at master bathy nodes in m

            # actually convert the bathy_data to the coordinates of the model!
            try:
                bc_coords = gp.FRFcoord(wavepacket['lon'], wavepacket['lat'])
            except:
                bc_coords = {'xFRF':max(master_bathy['xFRF']),'yFRF':0}
                print('Ty think about how to do this for locations away from duck')
            b_dict['BC_FRF_X'] = max(master_bathy['xFRF'])  # this is because I force the gauge to be at a grid node
            b_dict['BC_FRF_Y'] = 0
            # check that the gauge is inside my "master_bathy" x bounds
            assert bc_coords['xFRF'] <= max(master_bathy['xFRF']) and bc_coords['xFRF'] >= min(master_bathy[
                                                                                                   'xFRF']), 'The wave gauge selected as the boundary condition is outside the known bathymetry.'

            # make the shift from "master bathy" to model bathy convention (zero at forcing instrument and positive increasing towards shore)
            print("Ty:Check this grid setup")
            b_dict['x'] = np.flipud(b_dict['BC_FRF_X'] - master_bathy['xFRF'][
                np.argwhere(master_bathy['xFRF'] <= b_dict['BC_FRF_X'])].flatten())
            b_dict['zb'] = np.flipud(
                master_bathy['elev'][np.argwhere(master_bathy['xFRF'] <= b_dict['BC_FRF_X'])].flatten())
            #b_dict['x'] = np.flipud(int(round(bc_coords['xFRF'])) - master_bathy['xFRF'][
            #    np.argwhere(master_bathy['xFRF'] <= int(round(bc_coords['xFRF'])))].flatten())
            #b_dict['zb'] = np.flipud(
            #    master_bathy['elev'][np.argwhere(master_bathy['xFRF'] <= int(round(bc_coords['xFRF'])))].flatten())
            b_dict['fw'] = np.flipud(fric_fac * np.ones(b_dict[
                                                            'x'].size))  # cross-shore values of the bottom friction (just sets it to be fric_fac at every point in the array)


        else:
            pass

        return b_dict

    def trim_CSHOREbathy(self, bathypacket, wavepacket):

        """
        This function will just modify my bathy packet variables if they need to be modified because the wave gauge
        has changed
        :param bathypacket: bathypacket output from prep_CSHOREbathy
        :param wavepacket: wavepacket output from prep_CSHOREwaves
        :return: new bathypacket modified to move the wave gauge to the appropriate location
        """

        bc_coords = gp.FRFcoord(wavepacket['lon'], wavepacket['lat'])
        bathypacket['BC_FRF_X'] = int(round(bc_coords['xFRF']))  # this is because I force the gauge to be at a grid node
        bathypacket['BC_FRF_Y'] = bc_coords['yFRF']

        # if I was at the 8m but now I'm at the 6, I need to shave off some of my domain!
        nBC_x = bathypacket['x']
        nBC_zb = bathypacket['zb']
        nBC_fw = bathypacket['fw']

        # change the bc stuff so that 0 is at the 6m awac now, then drop all points with less than zero!
        nBC_x = nBC_x - (max(nBC_x) - bathypacket['BC_FRF_X'])
        keep_ind = np.where(nBC_x >= 0)
        nBC_zb = nBC_zb[keep_ind]
        nBC_fw = nBC_fw[keep_ind]
        nBC_x = nBC_x[keep_ind]

        # delete the old ones and re-assign
        del bathypacket['x']
        del bathypacket['zb']
        del bathypacket['fw']
        bathypacket['x'] = nBC_x
        bathypacket['zb'] = nBC_zb
        bathypacket['fw'] = nBC_fw

        return bathypacket

    def waveTree_CSHORE(self, wg8m, wg6m, model_times, start_time, prev_wg=None):
        """
        # this is just a simple function to alleviate some clutter in frontBackCSHORE.  It basically takes in the
        wave gauge data from the 8m and 6m gauges, as well as the prev wave gauge if one is available, then decides
        which data need to be used
        :param wg8m: wavepacket from getObs.getWaveSpec at the 8m array
        :param wg6m: wavepacket from getObs.getWaveSpec at the 6m array
        :param prev_wg: optional.  use this if you want to force it to the 6m array
        :return: the wave dictionary from prep_CSHOREwaves!  or None, if it bombed out
        """
        if 'name' not in list(wg8m.keys()):
            wg8m['name'] = 'FRF 8m Array'
        if 'name' not in list(wg6m.keys()):
            wg6m['name'] = 'FRF 6m AWAC'

        if (prev_wg is None) or (prev_wg == 'FRF 8m Array'):

            # Attempt to get 8m array first!!!
            try:
                wave_data = wg8m
                t_class = PrepDataTools()
                out_dict = t_class.prep_CSHOREwaves(wave_data, model_times, start_time)
            except:
                # If that craps out, try to get the 6m AWAC!!!
                try:
                    wave_data = wg6m
                    t_class = PrepDataTools()
                    out_dict = t_class.prep_CSHOREwaves(wave_data, model_times, start_time)
                except:
                    # If that doesn't work, you are done....
                    out_dict = None

        elif prev_wg == 'FRF 6m AWAC':
            # go straight to 6m awac
            try:
                wave_data = wg6m
                t_class = PrepDataTools()
                o_dict = t_class.prep_CSHOREwaves(wave_data, model_times, start_time)
            except:
                # If that doesn't work, you are done....
                out_dict = None

        else:
            pass

        return out_dict



