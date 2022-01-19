import os
import uuid
from glob import glob
from types import SimpleNamespace
from typing import Optional
import numpy as np
from astropy.io import fits as pyfits
from astropy.time import Time
from dkist_processing_pac.tag import tag
from dkist_processing_pac.data.required_params import elliptical
from dkist_processing_pac.data import S122, CONSTANTS, load_visp_keywords, load_cryo_keywords, load_dlnirsp_keywords

"""The following basic functions simply return Mueller matrices of the named optical element. Parameters of each 
element can be specified, where appropriate."""


def linear_retarder(t_ret, ret, b=0):
    # See "DKIST Polarization Calibration: Modeling of Calibration Unit elements" by C. Beck, April 2018
    b_factor = np.sqrt(1. - b**2 / 4.)

    return t_ret * np.array([[   1, b/2.,                       0,                      0],
                             [b/2.,    1,                       0,                      0],
                             [   0,    0,  b_factor * np.cos(ret), b_factor * np.sin(ret)],
                             [   0,    0, -b_factor * np.sin(ret), b_factor * np.cos(ret)]], dtype=np.float64)

def elliptical_retarder(t_ret, d_h, d_45, d_r):
    # See either "Mueller matrix of DKIST calibration unit retarders" or
    #  "DKIST Polarization Calibration: Modeling of Calibration Unit elements"
    # both April 2018 by C. Beck.

    d = np.sqrt(d_h**2 + d_45**2 + d_r**2)
    cosd = np.cos(d)
    sind = np.sin(d)

    m22 = (d_h**2 + cosd * (d_45**2 + d_r**2)) / d**2
    m23 = ((1 - cosd) * d_45 * d_h) / d**2 + sind * d_r / d
    m24 = ((1 - cosd) * d_h * d_r) / d**2 - sind * d_45 / d
    m32 = ((1 - cosd) * d_45 * d_h) / d**2 - sind * d_r / d
    m33 = (d_45**2 + cosd * (d_h**2 + d_r**2)) / d**2
    m34 = ((1 - cosd) * d_45 * d_r) / d**2 + sind * d_h / d
    m42 = ((1 - cosd) * d_h * d_r) / d**2 + sind * d_45 / d
    m43 = ((1 - cosd) * d_45 * d_r) / d**2 - sind * d_h / d
    m44 = (d_r**2 + cosd * (d_45**2 + d_h**2)) / d**2

    return t_ret * np.array([[1,   0,   0,   0],
                             [0, m22, m23, m24],
                             [0, m32, m33, m34],
                             [0, m42, m43, m44]], dtype=np.float64)

def polarizer(t_pol, py, px=1):
    # See "DKIST Polarization Calibration: Modeling of Calibration Unit elements" by C. Beck, April 2018
    p_factor = px**2 + py**2
    p_ratio = (px**2 - py**2) / p_factor
    UV_factor = 2 * px * py / p_factor
    return 0.5 * t_pol * p_factor * np.array([[      1, p_ratio,           0,           0],
                                              [p_ratio,       1,           0,           0],
                                              [      0,       0,   UV_factor,           0],
                                              [      0,       0,           0,   UV_factor]], dtype=np.float64)


def rotation(theta):
    return np.array([[1,                  0,                 0, 0],
                     [0,  np.cos(2 * theta), np.sin(2 * theta), 0],
                     [0, -np.sin(2 * theta), np.cos(2 * theta), 0],
                     [0,                  0,                 0, 1]], dtype=np.float64)


def mirror(x, tau):
    # See "Mueller matrix of a mirror or mirror group", C. Beck March 2018

    mirror = np.array([[1 + x**2, 1 - x**2,                    0,                   0],
                       [1 - x**2, 1 + x**2,                    0,                   0],
                       [0,               0,  2 * x * np.cos(tau), 2 * x * np.sin(tau)],
                       [0,               0, -2 * x * np.sin(tau), 2 * x * np.cos(tau)]], dtype=np.float64)
    return mirror / (1 + x**2)


class Drawer():
    """Drawer is used to aggregate a collection of images corresponding to a Polarization Calibration Sequence and
    distribute a Set of Calibration Curves (SoCC) from those images.

    Aggregation is achieved by simply loading all FITS files in a directory and reading the configuration of the
    Calibration Unit from header values. These values are formed into Calibration Sequence (CS) vectors that can be
    iterated over by e.g., the CUModel.

    Distribution of the actual data is handled by slicing into this class. Each slice will provide a SoCC for a given
    (x, y, l) location. The result will be a single array that is M x N where M is the number of modulator states and N
    is the number of steps in the CS.
    In addition to the detector data, this class generates a set of vectors that describe the configuration of the
    Telescope and Calibration Unit during each exposure in the aggregated data.

    Finally, multiple instances of Drawer can be concatenated simply with the + operator.

    Attributes
    (only those you might need)
    ----------
    instrument : str
        The name of the instrument used to take the data (upper case)

    nummod : int
        The total number of modulator states in each step

    numsteps : int
        The total number of steps in the CS

    shape : tuple
        The shape of a single data exposure

    theta_pol_steps : numpy.ndarray
        The polarizer angle at each step in the CS

    theta_ret_steps : numpy.ndarray
        The retarder angle at each step in the CS

    pol_in : numpy.ndarray
        Boolean array - was the polarizer in the beam at each step?

    ret_in : numpy.ndarray
        Boolean array - was the retarder in the beam at each step?

    timeobs : numpy.ndarray
        The DATE-OBS keyword for each step of the CS. Format is MJD

    date_bgn : float
        Time at the start of the CS. Format is MJD

    date_end : float
        Time at the end of the CS. Format is MJD

    wavelength : float
        Coarse wavelength band of observations (nm)

    azimuth : numpy.ndarray
        Telescope azimuth at each step in the CS

    elevation : numpy.ndarray
        Telescope elevation at each step in the CS

    table_angle : numpy.ndarray
        Coude table angle at each step in the CS

    I_clear : float
        Average of the means of any detected Clear CS steps. Useful for initializing I_sys fit value.

    Notes
    -----
    An example:

    # Load the data from 'visp_CS_dir'.
    >>> DRWR = Drawer('visp_CS_dir')

    # Look at the number of modulator states and number of CS steps
    >>> DRWR.nummod
    8

    >>> len(DRWR.theta_pol_steps)
    20

    # Grab the SoCC for the pixel at (10, 100, 0)
    >>> I = DRWR[10, 100, 0]
    >>> I.shape
    (8, 20)

    Data access is via astropy.io.fits and is therefore very memory-efficient.
    """

    def __init__(self, data_dir=None, suffix='.FITS', instrument=None, remove_I_trend=True, skip_darks=True):
        """Create a new class instance. Optionally, load data from a directory.

        Parameters
        ----------
        data_dir : str
            Location of a directory containing all data corresponding to a single Calibration Sequence

        suffix : str
             A filter string use to select specific files. The file mask is data_dir/*suffix

        instrument : str
            The "official" (ed: what the hell does that mean?) string of the instrument used to acquire the calibration
            data. Case insensitive.

        remove_I_trend : bool
            If True then any global intensity variations will be removed with a linear fit to any clear measurements. If
            the provided data set does not contain clear measurements this option has no effect.

        skip_darks : bool
            If True (default) then don't load any dark steps from the CS
        """
        if instrument is not None:
            self.instrument = instrument
            self.load_inst_keywords()
        else:
            self.instrument = ''
            self.camera = ''
            self.modid_key = None
            self.modnum_key = None
        self.data_list = []
        self.theta_pol_steps = np.array([])
        self.theta_ret_steps = np.array([])
        self.pol_in = np.array([], dtype=bool)
        self.ret_in = np.array([], dtype=bool)
        self.dark_in = np.array([], dtype=bool)
        self.timeobs = np.array([])
        self.nummod = 0
        self.numsteps = 0
        self.azimuth = np.array([])
        self.elevation = np.array([])
        self.table_angle = np.array([])
        self.date_bgn = np.inf
        self.date_end = -np.inf
        self.wavelength = 0.
        self.RN = 0.
        self.norm_func = np.poly1d([0., 1.])
        self.I_clear = 0.

        if data_dir is not None:
            self.load_from_dir(data_dir, suffix=suffix, skip_darks=skip_darks)

        if remove_I_trend:
            self.find_clears()
            self.fit_intensity_trend()

    def __add__(self, other):
        """Concatenate two Drawer objects.

        First, make sure the two object share relevant parameters and then just concatenate the rest of the attributes.

        Returns
        -------
        Drawer
            A new Drawer object
        """
        if self.instrument != other.instrument:
            raise ValueError('{} and {} appear to be from different instruments'.format(self, other))

        if self.nummod != other.nummod:
            raise ValueError('{} and {} do not have the same number of modulator states'.format(self, other))

        if self.wavelength != other.wavelength:
            raise ValueError('{} and {} were not taken at the same wavelength'.format(self, other))

        output = Drawer(instrument=self.instrument, remove_I_trend=False)

        if self.RN != other.RN:
            newRN = max([self.RN, other.RN])
            output.RN = newRN
            print('{}: Warning {} and {} do not have the same read noise. Setting to the highest ({})'.format(tag(),
                                                                                                              self,
                                                                                                              other,
                                                                                                              newRN))

        output.data_list = self.data_list + other.data_list
        output.theta_pol_steps = np.append(self.theta_pol_steps, other.theta_pol_steps)
        output.theta_ret_steps = np.append(self.theta_ret_steps, other.theta_ret_steps)
        output.pol_in = np.append(self.pol_in, other.pol_in)
        output.ret_in = np.append(self.ret_in, other.ret_in)
        output.dark_in = np.append(self.dark_in, other.dark_in)
        output.timeobs = np.append(self.timeobs, other.timeobs)
        output.azimuth = np.append(self.azimuth, other.azimuth)
        output.elevation = np.append(self.elevation, other.elevation)
        output.table_angle = np.append(self.table_angle, other.table_angle)
        output.date_bgn = min(self.date_bgn, other.date_bgn)
        output.date_end = max(self.date_end, other.date_end)
        output.numsteps = self.numsteps + other.numsteps
        output.nummod = self.nummod
        output.wavelength = self.wavelength

        return output

    def __repr__(self):

        return "<PolCal SoCC Drawer started at {} with (m,n) = ({}, {}) and shape = {}>".format(self.date_bgn,
                                                                                               self.nummod,
                                                                                               self.numsteps,
                                                                                               self.shape)

    @property
    def shape(self):
        """The shape of this objects 'data'.

        This is useful for those who will be using the slicing functionality and expect to be able to see the shape of
        these data.
        """
        data = self.data_list[0][1].data

        return data.shape

    def load_inst_keywords(self):

        if self.instrument.upper() == 'VISP':
            load_visp_keywords()
            self.modid_key = S122['ViSP_CurrentState']
            self.modnum_key = S122['ViSP_NumberOfModulatorStates']
        elif self.instrument.upper() == 'DLNIRSP':
            load_dlnirsp_keywords()
            self.modid_key = S122['DLN_CurrentState']
            self.modnum_key = S122['DLN_NumberOfModulatorStates']
        #TODO: Is this not CRYO-SP and CRYO-CI? I forget
        elif self.instrument.upper() == 'CRYO':
            load_cryo_keywords()
            self.modid_key = S122['CRSP_CurrentState']
            self.modnum_key = S122['CRSP_NumberOfModulatorStates']
        elif self.instrument.upper() == 'VTF':
            self.modid_key = S122['VTF_CurrentState']
            self.modnum_key = S122['VTF_NumberOfModulatorStates']
        else:
            raise ValueError('Could not find information for instrument {}'.format(self.instrument))

    def load_from_dir(self, data_dir, suffix='.FITS', skip_darks=True):
        """Load all images found in a given directory. Data are stored as a list of astropy.io.fits HDUList objects.

        In addition to loading the actual data, header values are also inspected to create vectors of the polarizer and
        retarder angles, telescope geometry, and observation times.

        Parameters
        ----------
        data_dir : str
            The location of the directory containing the data to load. Should contain all images related to a single CS

        suffix : str
            Only files that end in this suffix will be loaded from the directory.

        skip_darks : bool
            If True (default) then don't load any dark steps from the CS
        """
        filelist = sorted(glob('{}/*{}'.format(data_dir, suffix)))
        if len(filelist) == 0:
            raise FileNotFoundError('Could not find any files in {} with suffix {}'.format(data_dir, suffix))
        nummod_list = []

        ref_id = 0
        ref_hdu = pyfits.open(filelist[ref_id])
        while ref_hdu[0].header[S122['GOSLevel0']] in ['Dark', 'DarkShutter'] and skip_darks:
            ref_id += 1
            ref_hdu = pyfits.open(filelist[ref_id])

        if ref_hdu[1].header['NAXIS'] != 3:
            raise ValueError('Data do not appear to have 3 dimensions (NAXIS = {})'.format(ref_hdu[1].header['NAXIS']))
        ref_inst = ref_hdu[0].header[S122['Instrument']]

        # ref_cam = ref_hdu[0].header[S122['CameraName']]
        ref_start = ref_hdu[0].header['DATE-BGN']
        ref_end = ref_hdu[0].header['DATE-END']
        ref_wave = ref_hdu[0].header[S122['Wavelength']]
        ref_hdu.close()

        self.instrument = ref_inst
        # self.camera = ref_cam
        self.load_inst_keywords()

        RN_list = []
        numsteps = 0
        for f in filelist:
            hdus = pyfits.open(f)
            if hdus[0].header[S122['GOSLevel0']] in ['Dark', 'DarkShutter']:
                try:
                    RN_list.append(hdus[0].header[S122['ReadNoise']])
                except KeyError:
                    print('{}: Found no read noise information in DARK step {}'.format(tag(), f))
                if skip_darks:
                    print('{}: skipping DARK step {}'.format(tag(), f))
                    continue

            if hdus[1].header['NAXIS'] != 3:
                raise ValueError(
                        'Data do not appear to have 3 dimensions (NAXIS = {})'.format(ref_hdu[1].header['NAXIS']))

            if hdus[0].header[S122['Instrument']] != ref_inst:
                raise ValueError('Not all input files were taken with the same instrument')

            # if hdus[0].header[S122['CameraName']] != ref_cam:
            #     raise ValueError('Not all input files were taken with the same camera')

            # if hdus[0].header['DATE-BGN'] != ref_start or hdus[0].header['DATE-END'] != ref_end:
            #     raise ValueError('Not all input files have the same start/end dates')

            if hdus[0].header[S122['Wavelength']] != ref_wave:
                raise ValueError('Not all input files were taken at the same wavelength')

            self.azimuth = np.append(self.azimuth, hdus[0].header['TAZIMUTH'])
            self.elevation = np.append(self.elevation, hdus[0].header['TELEVATN'])
            self.table_angle = np.append(self.table_angle, hdus[0].header['TTBLANGL'])

            self.theta_pol_steps = np.append(self.theta_pol_steps, float(hdus[0].header[S122['PolarizerAngle']]))
            self.theta_ret_steps = np.append(self.theta_ret_steps, float(hdus[0].header[S122['RetarderAngle']]))
            self.pol_in = np.append(self.pol_in, hdus[0].header[S122['GOSPolarizer']] not in ['undefined', 'clear', False])
            self.ret_in = np.append(self.ret_in, hdus[0].header[S122['GOSRetarder']] not in ['undefined', 'clear', False])
            self.dark_in = np.append(self.dark_in, hdus[0].header[S122['GOSLevel0']] in ['Dark', 'DarkShutter'])

            try:
                time = Time(hdus[0].header['DATE-OBS'])
            except ValueError:
                raise ValueError('Could not parse date header date {} from {}'.format(hdus[0].header['DATE-OBS'], f))
            self.timeobs = np.append(self.timeobs, time.mjd)

            nummod_list.append(hdus[0].header[self.modnum_key])
            self.data_list.append(hdus)
            numsteps += 1

        if np.unique(nummod_list).size != 1:
            raise ValueError('Not all input files have the same number of modulator states')

        if len(RN_list) > 0:
            self.RN = np.mean(RN_list)
            print('{:}: Noise floor read to be {:.2f}'.format(tag(), self.RN))
        else:
            print('{}: Could not find Read Noise information for Drawer...'.format(tag()))
            self.RN = self.get_fallback_noise_floor(ref_hdu)

        self.nummod = nummod_list[0]
        self.numsteps += numsteps
        self.date_bgn = min(self.date_bgn, Time(ref_start, format='fits').mjd)
        self.date_end = max(self.date_end, Time(ref_end, format='fits').mjd)
        self.wavelength = ref_wave

    def find_clears(self):
        """Identify which HDUList objects contain clear observations and populate self.clears

        A clear frame is defined as one in which both the polarizer and retarder were out of the light path.
        """
        clears = []
        clear_times = np.array([])
        for i, h in enumerate(self.data_list):
            if not self.pol_in[i] and not self.ret_in[i] and not self.dark_in[i]:
                clears.append(h)
                clear_times = np.append(clear_times, self.timeobs[i])

        self.clears = clears
        self.clear_times = clear_times

    def fit_intensity_trend(self):
        """Use clear frames to fit and remove any global intensity trends.

        The flux in each clear is averaged over all modulation states and the set of all clears is used to fit a linear
        trend of flux vs time. This line is then divided from all data, including clears.

        Note that because the absolute offset (i.e., intercept) is also fit the overall intensity is normalized by
        something very close to the flux in the first clear measurement.
        """
        try:
            avg_clear_flux = np.zeros(len(self.clears))
        except AttributeError:
            print('{}: WARNING: clear frames have not yet been identified. Use .find_clears() to do so'.format(tag()))
            return
        if len(self.clears) == 0:
            print('{}: WARNING: this Drawer does not contain any clear measurements. No correction is possible.'.format(tag()))
            return

        # First, get the linear trend in clear intensity
        for i, h in enumerate(self.clears):
            tmp = 0.
            for j in range(self.nummod):
                tmp += np.nanmean(h[j + 1].data)
            avg_clear_flux[i] = tmp / self.nummod

        self.I_clear = np.mean(avg_clear_flux)
        print('{}: Average flux in clear measurements (I_clear): {:<10.3f}'.format(tag(), self.I_clear))
        if self.I_clear < CONSTANTS['min_clear_flux']:
            raise ValueError('Flux in Clear measurements is too low ({:.2f} < {:.2f})'.format(self.I_clear,
                                                                                              CONSTANTS['min_clear_flux']))
        fit = np.poly1d(np.polyfit(self.clear_times, avg_clear_flux, 1)) / self.I_clear
        self.norm_func = fit


    def __getitem__(self, item):
        """This builtin method provides the mechanism by which the object can be sliced to provided a single SoCC.

        The slice must have two elements (x, y, l). E.g.:

        >>> I = DRWR[x, y, l]

        Parameters
        ----------
        item : tuple
            The (x, y, l) position tuple. Don't worry, python's slicing syntax will take care of this for you.

        Returns
        -------
        numpy.ndarray
            A 2D array of shape (M, N) where M is the number of modulator states and N is the number of steps in the
            Calibration Sequence.

        """
        if type(item) is not tuple or len(item) != 3:
            raise IndexError('Drawer must be indexed by exactly three values')

        xpos, ypos, lpos = item

        if not np.issubdtype(type(xpos), np.integer) \
                or not np.issubdtype(type(ypos), np.integer) \
                or not np.issubdtype(type(lpos), np.integer):
            raise IndexError('Only integers are allowed as valid indices')

        result = np.zeros((self.nummod, self.numsteps), dtype=np.float64)

        for n in range(self.numsteps):
            hdus = self.data_list[n]
            modnums = np.array([h.header[self.modid_key] for h in hdus[1:]])
            for m in range(self.nummod):
                idx = np.where(modnums == m + 1)[0][0]
                result[m, n] = hdus[idx + 1].data[xpos, ypos, lpos] / self.norm_func(self.timeobs[n])
                del hdus[idx + 1].data

        return result

    def get_uncertainty(self, data: np.ndarray) -> np.ndarray:
        """Right now this just computes a very simply noise estimate. In the future it will be able to read from
        uncertainty frames provided by the IPAs"""

        return np.sqrt(np.abs(data) + self.RN**2)

    def get_fallback_noise_floor(self, hdu: pyfits.HDUList) -> float:
        """Used to provide a absolute last-resort noise floor if the instruments haven't provided their own
        """

        noise_floor_dict = CONSTANTS['Fallback_noise_floors']
        if self.instrument.upper() == 'VISP':
            noise_floor = noise_floor_dict['VISP']

        elif self.instrument.upper() == 'DLNIRSP':
            print('$$', self.camera)
            if self.camera == 'DLVIS':
                noise_floor = noise_floor_dict['DLNIRSP_VIS']
            elif self.camera == 'DLNIR':
                noise_floor = noise_floor_dict['DLNIRSP_NIR']
            else:
                raise ValueError('Could not find entry for DLNIRSP camera {}'.format(self.camera))

        elif self.instrument.upper() == 'CRYO':
            cryo_inst = hdu[0].header[S122['CRSP_CryoInstrument']]
            if cryo_inst == 1:
                noise_floor = noise_floor_dict['CRYO_SP']
            elif cryo_inst == 2:
                noise_floor = noise_floor_dict['CRYO_CI']
            else:
                raise ValueError('Could not find entry for Cryo instrument {}'.format(cryo_inst))

        elif self.instrument.upper() == 'VTF':
            noise_floor = noise_floor_dict['VTF']

        else:
            noise_floor = noise_floor_dict['Last_resort']
            print('{}: Could not figure out what noise floor to use for instrument "{}". '
                  'Falling back to default value.'.format(tag(), self.instrument))

        print('{:}: Using default noise floor of {:.2f}'.format(tag(), noise_floor))

        return noise_floor

    def plot_curves(self, output, location=None):
        """Plot Calibration Curves for all points in the data set

        Each (x, y, l) location will be given a separate plot containing overplots of all modulation states

        Parameters
        ----------
        output : str
            Location to save plot file
        """
        from cycler import cycler
        import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages as PDF
        matplotlib.style.use('classic')

        matplotlib.rc('axes', prop_cycle=cycler(color=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c',
                  '#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928']))

        numx, numy, numl = self.shape
        if location is not None:
            x_range = [location[0]]
            y_range = [location[1]]
            l_range = [location[2]]
        else:
            x_range = range(numx)
            y_range = range(numy)
            l_range = range(numl)

        pp = PDF(output)
        for i in x_range:
            for j in y_range:
                for k in l_range:
                    ax = plt.figure().add_subplot(111)
                    ax.set_xlabel('CS step')
                    ax.set_ylabel('Counts')
                    d = self[i, j, k]
                    for m in range(self.nummod):
                        ax.plot(d[m])
                    ax.set_title('[{}, {}, {}]'.format(i, j, k))
                    pp.savefig(ax.figure)
                    del d

        pp.close()
        plt.close('all')

class Dresser():
    """Dresser is, quite simply, a collection of Drawer objects. It's primary function is to allow the
    `FittingFramework` to not have to worry about how many Drawers the user has provided for, e.g., fitting the M36
    group parameters.

    This class doesn't do much except keep track of the Drawers and concatenate a StoCCinG when a user asks for a
    specific location.

    Its attributes are basically the same as those of Drawer

    Attributes
    (only those you might need)
    ----------
    instrument : str
        The name of the instrument used to take the data (upper case)

    nummod : int
        The total number of modulator states in each step

    numsteps : int
        The total number of steps in all CS's across all Drawers

    shape : tuple
        The shape of a single data exposure

    theta_pol_steps : numpy.ndarray
        The polarizer angle at each CS step

    theta_ret_steps : numpy.ndarray
        The retarder angle at each CS step

    pol_in : numpy.ndarray
        Boolean array - was the polarizer in the beam at each step?

    ret_in : numpy.ndarray
        Boolean array - was the retarder in the beam at each step?

    date_bgn : float
        Time at the start of the CS of the first Drawer. Format is MJD

    date_end : float
        Time at the end of the CS of the last Drawer. Format is MJD

    wavelength : float
        Coarse wavelength band of observations (nm)

    azimuth : numpy.ndarray
        Telescope azimuth at each CS step

    elevation : numpy.ndarray
        Telescope elevation at each CS step

    table_angle : numpy.ndarray
        Coude table angle at each CS step

    I_clear : float
        Average of the means of any detected Clear CS steps. Useful for initializing I_sys fit value.
    """

    def __init__(self):
        """Create a new class instance. This is easy; just initialize all the arrays that might eventually hold stuff.
        """
        self.drawers = []
        self.azimuth = np.array([])
        self.elevation = np.array([])
        self.table_angle = np.array([])
        self.theta_pol_steps = np.array([])
        self.theta_ret_steps = np.array([])
        self.pol_in = np.array([], dtype=bool)
        self.ret_in = np.array([], dtype=bool)
        self.dark_in = np.array([], dtype=bool)
        self.delta_t = np.array([])
        self.nummod = 0
        self.numsteps = 0
        self.date_bgn = np.inf
        self.date_end = -np.inf
        self.wavelength = 0.
        self.instrument = None
        self.shape = ()

    def __repr__(self):

        rprstr = "<PolCal Dresser with (m,n) = ({}, {}) and the following Drawers:\n".format(self.nummod, self.numsteps)
        for d in self.drawers:
            rprstr += " {}\n".format(d)
        rprstr += ">"

        return rprstr

    @property
    def numdrawers(self):
        """The number of Drawers (AKA CS's) in this Dresser

        Returns
        -------
        int
        """
        return len(self.drawers)

    @property
    def drawer_step_list(self):
        """The number of CS steps in each Drawer

        Returns
        -------
        list
        """
        return [d.numsteps for d in self.drawers]

    def add_drawer(self, drawer: Drawer):
        """Add a Drawer to the Dresser

        Checks are made to ensure the Drawer fits in the Dresser (correct instrument, number of positions, etc.), and
        the CS configuration vectors are updated to include information from the new Drawer.

        Parameters
        ----------
        drawer : `Data.Drawer`
            PolCal Data from a single CS
        """
        if self.nummod == 0:
            self.nummod = drawer.nummod
        else:
            if drawer.nummod != self.nummod:
                raise ValueError('Trying to add Drawer with {} mod states to Dresser with {}'.format(drawer.nummod,
                                                                                                     self.nummod))

        if self.wavelength == 0.:
            self.wavelength = drawer.wavelength
        else:
            if drawer.wavelength != self.wavelength:
                raise ValueError('Drawer with wave = {:6.1f} cannot be added to Dresser with wave = {:6.1f}'.\
                                 format(drawer.wavelength, self.wavelength))

        if self.instrument is None:
            self.instrument = drawer.instrument
        else:
            if drawer.instrument != self.instrument:
                raise ValueError('Drawer from instrument {} cannot be added to Dresser from instrument {}'.\
                                 format(drawer.instrument, self.instrument))

        if self.shape == ():
            self.shape = drawer.shape
        else:
            if drawer.shape != self.shape:
                raise ValueError('Drawer with shape {} does not fit into Dresser with shape {}'.format(drawer.shape,
                                                                                                       self.shape))

        self.drawers.append(drawer)
        for attr in ['azimuth', 'elevation', 'table_angle', 'theta_pol_steps',
                     'theta_ret_steps', 'pol_in', 'ret_in', 'dark_in']:
            setattr(self, attr, np.append(getattr(self, attr), getattr(drawer, attr)))

        self.delta_t = np.append(self.delta_t, drawer.timeobs - np.min(drawer.timeobs))

        self.date_bgn = min(self.date_bgn, drawer.date_bgn)
        self.date_end = max(self.date_end, drawer.date_end)
        self.numsteps += drawer.numsteps


    @property
    def I_clear(self):
        """The I_clear property for each Drawer

        Returns
        -------
        `numpy.ndarray`
        """
        I_clear = np.empty((self.numdrawers,), dtype=np.float64)
        for i, d in enumerate(self.drawers):
            I_clear[i] = d.I_clear

        return I_clear

    def __getitem__(self, item):
        """Concatenate all the SoCCs at the same position from each Drawer.

        We call this a Set of Calibration Curves in a Group (a StoCCinG).

        Parameters
        ----------
        item: tuple
            The (x, y, l) position tuple. Don't worry, python's slicing syntax will take care of this for you.

        Returns
        -------
        numpy.ndarray
            Array of shape (M, N) where M is the number of modulator states and N is the total number of steps across
            all CS's in all Drawers.
        """
        data = np.empty((self.nummod, self.numsteps), dtype=np.float64)
        uncertainty = np.empty(data.shape, dtype=np.float64)

        xpos, ypos, lpos = item

        idx = 0
        for d in self.drawers:
            drawer_data = d[xpos, ypos, lpos]
            data[:, idx:idx + d.numsteps] = drawer_data
            uncertainty[:, idx:idx + d.numsteps] = d.get_uncertainty(drawer_data)
            idx += d.numsteps

        return data, uncertainty

class CUModelParams():
    """A container for CU Model parameters. The primary functions of this object are to write a FITS file that contains
    these parameters in a format that allows Instrument Partners to resample them to whatever field they need and to
    load a set of parameters after they have been resampled.

    The CU parameters are kept in a 3D array of shape (X, Y, L, Z) where (X, Y, L) is the shape of the FOV present in
    the Drawer(s) used in fitting and Z is the number of CU parameters (fixed and free).
    """

    def __init__(self,
                 x: int,
                 y: int,
                 l: int,
                 numdrawers: int,
                 nummod: int,
                 fit_mode: str = 'baseline',
                 init_set: str = 'default',
                 header: Optional[pyfits.header.Header] = None):
        """Initialize the object. All this does is create the empty array that will hold CU parameters.

        Parameters
        ----------
        x : int
            Number of field spatial positions in the x direction

        y : int
            Number of field spatial positions in the y direction

        l : int
            Number of field positions in the l dimension

        numdrawers : int
            Total number of Drawers that were used to fit CU parameters. This is greater than 1 when fitting Telescope
            M36 group parameters

        fit_mode : str
            Name of the PA&C fitting recipe used to produce the CU parameters

        init_set : str
            Name of the initial value set used to produce CU parameters

        header : `astropy.io.fits.header.Header`
            If provided, this object will be initialized with this header
        """
        self.shape = (x, y, l)
        self.numdrawers = numdrawers
        self.nummod = nummod

        numparams = numdrawers * (len(self.required['params']) - len(self.required['global'])) + len(self.required['global'])
        numparams += nummod * 4
        self.fit_mode = fit_mode
        self.init_set = init_set
        self.tmp_name = 'tmpCU_pars_{}.fits'.format(uuid.uuid4().hex)

        self._init_tmp_file(numparams, x, y, l, header=header)

        self.hdu_list = pyfits.open(self.tmp_name, mode='update')
        self.CU_params = self.hdu_list[0].data

    def __del__(self):
        """This is only here to be nice to any developers/testers who forget to call cleanup().
        In general, it is bad practice to rely on this method and cleanup() should be called explicitly.
        """
        try:
            self.cleanup()
        except:
            pass

    def _init_tmp_file(self, numparams, x, y, l, header=None):
        """Initialize a temp FITS file that will store the CU Parameters. We do this so that a a single file descriptor
        is used every time __setitem__ is called an the results are flushed to disk.

        Parameters
        ----------
        numparams : int
            The number of fit parameters

        x, y, l : int
            The shape of the Dresser

        header : `astropy.io.fits.header.Header`
            If provided, initialize the tmp file with this header
        """
        tmp_ph = pyfits.PrimaryHDU(np.zeros((x, y, l, numparams)), header=header)
        tmp_ph.header['PACFMODE'] = self.fit_mode
        tmp_ph.header['INITSET'] = self.init_set
        i = 0
        for p in self.required['global']:
            tmp_ph.header['CUPAR{:03n}'.format(i)] = (p, 'CU parameter index {}'.format(i))
            i += 1
        for j in range(self.numdrawers):
            for p in self.required['params']:
                if p in self.required['global']:
                    continue
                tmp_ph.header['CUPAR{:03n}'.format(i)] = ('{:}_CS{:02n}'.format(p, j),
                                                           'CU parameter index {} for CS {}'.format(i, j))
                i += 1
        for m in range(self.nummod):
            for s in ['I', 'Q', 'U', 'V']:
                tmp_ph.header['CUPAR{:03n}'.format(i)] = ('modmat_{}{}'.format(m,s),
                                                          'Modulation matrix entry {} -> {}'.format(m, s))
                i += 1

        tmp_ph.writeto(self.tmp_name)
        del tmp_ph.data
        del tmp_ph

    @property
    def required(self):
        return elliptical

    @property
    def par_names(self):
        """A list containing the names of the parameters that correspond to the last axis of self.CU_params"""
        names = self.required['global'][:]
        for i in range(self.numdrawers):
            names += ['{:}_{:02n}'.format(p, i) for p in self.required['params'] if p not in self.required['global']]

        for m in range(self.nummod):
            for s in ['I', 'Q', 'U', 'V']:
                names += ['modmat_{}{}'.format(m,s)]

        return names

    def __repr__(self):
        return "<CUModelParams with shape ({}, {}, {}, {}) from {} Drawers with {} fitting recipe>".\
            format(*list(self.CU_params.shape) + [self.numdrawers, self.fit_mode])

    def __setitem__(self, key, value):
        """Insert a set of fit parameters from a SoCC or StoCCinG into the CU parameter array.

        Every time an item is set, the current object will be written to disk. This is a somewhat janky way to ensure
        that a crash on looong fits does not result in a total loss of fit results.

        Parameters
        ----------
        key : tuple
            The (x, y, l) spatial location of the SoCC or StoCCinG

        value : `lmfit.MinimizerResult`
            The fitting object that is produced by lmfit's `minimize` function. It contains the best-fit CU parameters.
        """
        xpos, ypos, lpos = key

        if value is None:
            cu_pars = np.zeros(self.CU_params.shape[3])
            cu_pars[-self.nummod * 4::4] = 1. / self.nummod

        else:
            pardict = value.params.valuesdict()
            cu_pars = np.array([pardict[p] for p in self.required['global']])
            for i in range(self.numdrawers):

                cu_pars = np.append(cu_pars,
                                    np.array([pardict['{:}_CS{:02n}'.format(p,i)] \
                                              for p in self.required['params'] if p not in self.required['global']]))

            for m in range(self.nummod):
                for s in ['I', 'Q', 'U', 'V']:
                    cu_pars = np.append(cu_pars, pardict['modmat_{}{}'.format(m, s)])

        self.CU_params[xpos, ypos, lpos, :] = cu_pars
        self.hdu_list.flush()

    def __getitem__(self, item):
        """Use the currently loaded CU parameters to generate a dictionary of parameter : value pairs.

        This dictionary is intended for use in initializing a `CUModel.CalibrationSequence` object with the best-fit
        CU parameters.

        Parameters
        ----------
        item : tuple
            (x, y, l) location of the CU parameters to load

        Returns
        -------
        dict
            Dictionary of parameter : value pairs for all parameters in the CU model
        """
        xpos, ypos, lpos = item

        params = {}
        i = 0
        for p in self.required['global']:
            params[p] = self.CU_params[xpos, ypos, lpos, i]
            i += 1
        for j in range(self.numdrawers):
            for p in self.required['params']:
                if p in self.required['global']:
                    continue
                params['{:}_CS{:02n}'.format(p, j)] = self.CU_params[xpos, ypos, lpos, i]
                i += 1

        for m in range(self.nummod):
            for s in ['I', 'Q', 'U', 'V']:
                params['modmat_{}{}'.format(m, s)] = self.CU_params[xpos, ypos, lpos, i]
                i += 1

        return params

    def writeto(self, filename, header=None, overwrite=True):
        """Write the CU parameters to a FITS file

        The FITS file will have a single HDU with a (X, Y, L, Z). Any header provided will be updated to include the
        parameter names for each entry along the Z dimension. If no header is provided a blank one will be created.

        Parameters
        ----------
        filename : str
            Path to save the FITS file

        header : `astropy.io.fits.header.Header`
            An optional header to add to the FITS file. It will be updated with information about the parameter names

        overwrite : bool
            If False then an error will be raised if filename already exists
        """
        if header is not None:
            self.hdu_list[0].header.update(header)

        self.hdu_list.writeto(filename, overwrite=overwrite)

    def loadfits(self, filename):
        """Read CU parameters from a FITS file

        The FITS file should have a single HDU with an (X, Y, L, Z) array. The header MUST contain the header keywords
        generated by `writeto`; these are compared with the parameter list to verify the format/usefulness of the file.

        Parameters
        ----------
        filename : str
            Location of the FITS file to read. Should probably exist.
        """
        self.hdu_list = pyfits.open(filename)

        try:
            self.fit_mode = self.hdu_list[0].header['PACFMODE']
        except KeyError:
            raise KeyError('Could not determine which fitting recipe was used to produce parameters in {}'.format(filename))

        try:
            self.init_set = self.hdu_list[0].header['INITSET']
        except KeyError:
            raise KeyError('Could not determine which initial value set was used to produce parameters in {}'.format(filename))

        i = 0
        for p in self.required['global']:
            if self.hdu_list[0].header['CUPAR{:03n}'.format(i)] != p:
                raise ValueError('Parameter file is misformed for parameter {}'.format(p))
            i += 1
        for j in range(self.numdrawers):
            for p in self.required['params']:
                if p in self.required['global']:
                    continue
                if self.hdu_list[0].header['CUPAR{:03n}'.format(i)] != '{:}_CS{:02n}'.format(p, j):
                    raise ValueError('Parameter file is misformed for paramter {:}_CS{:02n}'.format(p, j))
                i += 1

        self.CU_params = self.hdu_list[0].data
        self.shape = self.CU_params.shape[:-1]

    def cleanup(self):
        """Remove the temporary file used to hole intermediate results every time __setitem__ was called."""
        os.remove(self.tmp_name)

class TelescopeModelParams():
    """A container for Telescope Model parameters. The primary functions of this object are to write a FITS file that
    contains these parameters in a format that allows Instrument Partners to resample them to whatever field they need
    and to load a set of parameters after they have been resampled.

    The TM parameters are kept in a 3D array of shape (X, Y, L, 6) where (X, Y, L) is the shape of the FOV present in
    the StoCCinG used in fitting.
    """

    def __init__(self, x, y, l, header=None):
        """Initialize the object. All this does is create the empty array that will hold TM parameters.

        Parameters
        ----------
        x : int
            Number of field spatial positions in the x direction

        y : int
            Number of field spatial positions in the y direction

        l : int
            Number of field positions in the l dimension

        header : `astropy.io.fits.header.Header`
            If provided, this object will be initialized with this header
        """
        self.shape = (x, y, l)
        self.tmp_name = 'tmpTM_pars_{}.fits'.format(uuid.uuid4().hex)

        self._init_tmp_file(x, y, l, header=header)

        self.hdu_list = pyfits.open(self.tmp_name, mode='update')
        self.TM_params = self.hdu_list[0].data

    def __del__(self):
        """This is only here to be nice to any developers/testers who forget to call cleanup().
        In general, it is bad practice to rely on this method and cleanup() should be called explicitly.
        """
        try:
            self.cleanup()
        except:
            pass

    def _init_tmp_file(self, x, y, l, header=None):
        """Initialize a temp FITS file that will store the CU Parameters. We do this so that a a single file descriptor
        is used every time __setitem__ is called an the results are flushed to disk.

        Parameters
        ----------
        numparams : int
            The number of fit parameters

        x, y : int
            The shape of the Dresser

        header : `astropy.io.fits.header.Header`
            If provided, initialize the tmp file with this header
        """
        tmp_ph = pyfits.PrimaryHDU(np.zeros((x, y, l, 6)), header=header)
        tmp_ph.header['TMPAR000'] = 'X_12'
        tmp_ph.header['TMPAR001'] = 'tau_12 [rad]'
        tmp_ph.header['TMPAR002'] = 'X_34'
        tmp_ph.header['TMPAR003'] = 'tau_34 [rad]'
        tmp_ph.header['TMPAR004'] = 'X_56'
        tmp_ph.header['TMPAR005'] = 'tau_56 [rad]'

        tmp_ph.writeto(self.tmp_name)

        del tmp_ph.data
        del tmp_ph

    def __repr__(self):
        return "<TelescopeModelParams with shape ({}, {}, {})>".\
            format(*list(self.TM_params.shape))

    def __setitem__(self, key, value):
        """Insert a set of fit parameters from a SoCC or StoCCinG into the TM parameter array.

        Every time an item is set, the current object will be written to disk. This is a somewhat janky way to ensure
        that a crash on looong fits does not result in a total loss of fit results.

        Parameters
        ----------
        key : tuple
            The (x, y, l) spatial location of the SoCC or StoCCinG

        value : `PAC_Pipeline.TelescopeModel.TelescopeModel`
            The best-fit Telescope Model
        """
        xpos, ypos, lpos = key

        if value is None:
            value = SimpleNamespace(**{'x12': 0, 't12': 1,
                                       'x34': 0, 't34': 1,
                                       'x56': 0, 't56': 1})

        self.TM_params[xpos, ypos, lpos, 0] = value.x12
        self.TM_params[xpos, ypos, lpos, 1] = value.t12
        self.TM_params[xpos, ypos, lpos, 2] = value.x34
        self.TM_params[xpos, ypos, lpos, 3] = value.t34
        self.TM_params[xpos, ypos, lpos, 4] = value.x56
        self.TM_params[xpos, ypos, lpos, 5] = value.t56

        self.hdu_list.flush()

    def __getitem__(self, item):
        """Use the currently loaded TM parameters to generate list of TM mirror parameters.

        Parameters
        ----------
        item : tuple
            (x, y, l) location of the CU parameters to load

        Returns
        -------
        list
            List of TM mirror parameters: [x12, t12, x34, t34, x56, t56]
        """
        xpos, ypos, lpos = item

        return self.TM_params[xpos, ypos, lpos, :]

    def writeto(self, filename, header=None, overwrite=True):
        """Write the TM parameters to a FITS file

        The FITS file will have a single HDU with a (X, Y, L, 6). Any header provided will be updated to include the
        parameter names for each entry along the last dimension. If no header is provided a blank one will be created.

        Parameters
        ----------
        filename : str
            Path to save the FITS file

        header : `astropy.io.fits.header.Header`
            An optional header to add to the FITS file. It will be updated with information about the parameter names

        overwrite : bool
            If False then an error will be raised if filename already exists
        """
        if header is not None:
            self.hdu_list[0].header.update(header)

        self.hdu_list[0].writeto(filename, overwrite=overwrite)

    def loadfits(self, filename):
        """Read TM parameters from a FITS file

        The FITS file should have a single HDU with an (X, Y, L, 6) array.

        Parameters
        ----------
        filename : str
            Location of the FITS file to read. Should probably exist.
        """
        self.hdu_list = pyfits.open(filename)
        self.TM_params = self.hdu_list[0].data
        self.shape = self.TM_params.shape[:-1]

    def cleanup(self):
        """Remove the temporary file used to hole intermediate results every time __setitem__ was called."""
        os.remove(self.tmp_name)
